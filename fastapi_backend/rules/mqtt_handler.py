import os
import json
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt
from database import SessionLocal
from rooms.models import Room
from devices.models import Device, DeviceField, Telemetry, HealthStatusEnum
from .models import Command
from .rule_engine import RuleEngine
from notifications.processor import (
    process_device_online_notification, 
    process_device_offline_notification,
    process_device_misconfigured_notification
)

logger = logging.getLogger(__name__)

# MQTT config
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USERNAME", "")
MQTT_PASS = os.getenv("MQTT_PASSWORD", "")

# Offline timeout in seconds
OFFLINE_TIMEOUT = 30 

class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        if MQTT_USER and MQTT_PASS:
            self.client.username_pw_set(MQTT_USER, MQTT_PASS)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connected = False
        self.rule_engine = RuleEngine()
        self.last_seen: Dict[str, float] = {}
        self.last_seen_lock = threading.Lock()
        threading.Thread(target=self._auto_offline_loop, daemon=True).start()

    def _on_connect(self, client, userdata, flags, rc):
        self.connected = (rc == 0)
        print("✅ MQTT connected" if self.connected else f"❌ MQTT connect failed: {rc}")
        if self.connected:
            client.subscribe("iot/+/data")
            client.subscribe("iot/+/ack")
            print("🔔 Subscribed iot/+/data & iot/+/ack")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        parts = topic.split("/")
        if len(parts) < 3:
            return
        
        ma_phong, kind = parts[1], parts[2]
        try:
            payload = json.loads(msg.payload.decode() or "{}")
            if kind == "data":
                self._handle_data(ma_phong, payload)
            elif kind == "ack":
                self._handle_ack(payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message on topic {topic}: {e}")


    def _handle_data(self, ma_phong: str, data: Dict[str, Any]):
        db = SessionLocal()
        try:
            device_id = data.get("device_id")
            sensor_data = data.get("data") or {}
            if not device_id or not sensor_data:
                return

            room = db.query(Room).filter(Room.ma_phong == ma_phong).first()
            if not room: return

            dev = db.query(Device).filter(Device.ma_thiet_bi == device_id, Device.phong_id == room.id).first()
            if not dev: return

            # === LOGIC XỬ LÝ HEALTH STATUS BẮT ĐẦU TỪ ĐÂY ===

            valid_fields_query = db.query(DeviceField.khoa).filter(DeviceField.thiet_bi_id == dev.id).all()
            expected_fields = {item.khoa for item in valid_fields_query}
            incoming_fields = set(sensor_data.keys())

            # Kiểm tra nếu có trường không hợp lệ
            if not incoming_fields.issubset(expected_fields):
                invalid_fields = incoming_fields - expected_fields
                logger.warning(f"Device {device_id} sent invalid fields: {invalid_fields}")

                # QUAN TRỌNG: Chỉ hành động nếu trạng thái trước đó là 'ok'
                if dev.health_status == HealthStatusEnum.ok:
                    dev.health_status = HealthStatusEnum.misconfigured
                    db.commit() # Lưu ngay trạng thái mới

                    # Kích hoạt gửi một thông báo duy nhất
                    threading.Thread(
                        target=process_device_misconfigured_notification, 
                        args=(device_id, list(invalid_fields))
                    ).start()
                
                # Dừng xử lý gói tin sai này
                return
            else:
                # Nếu dữ liệu đúng, kiểm tra xem có cần đổi trạng thái về 'ok' không
                if dev.health_status == HealthStatusEnum.misconfigured:
                    dev.health_status = HealthStatusEnum.ok
                    # Trạng thái sẽ được commit chung ở dưới

            # === KẾT THÚC LOGIC HEALTH STATUS ===
            
            # Phần code xử lý dữ liệu và rule engine như cũ
            was_offline = dev.trang_thai == "online" # Note: Check for 'online' status
            dev.last_seen = datetime.utcnow()
            dev.trang_thai = "online"

            # ... (code xử lý online/offline notification) ...

            for k, v in sensor_data.items():
                db.add(Telemetry(thiet_bi_id=dev.id, khoa=k, gia_tri=str(v)))
            
            db.commit() # Commit tất cả thay đổi (bao gồm cả health_status về 'ok')

            with self.last_seen_lock:
                self.last_seen[device_id] = time.time()
            
            self.rule_engine.evaluate_rules(
                db, room_id=room.id, device_id=device_id, sensor_data=sensor_data
            )
            
            logger.info(f"✅ Data processed from {device_id}: {sensor_data}")

        except Exception as e:
            db.rollback()
            logger.error(f"❌ handle_data error for {device_id}: {e}", exc_info=True)
        finally:
            db.close()

    def _handle_ack(self, data: Dict[str, Any]):
        cmd_id = data.get("cmd_id")
        if not cmd_id: return
        db = SessionLocal()
        try:
            cmd = db.query(Command).filter(Command.id == cmd_id).first()
            if not cmd: return
            
            status = data.get("status", "unknown")
            if status == "ok":
                cmd.status = "acked"
                cmd.acked_at = datetime.utcnow()
            else:
                cmd.status = "failed"
                cmd.error_message = data.get("message", "Device error")
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"❌ handle_ack error for cmd_id {cmd_id}: {e}")
        finally:
            db.close()

    def _auto_offline_loop(self):
        while True:
            time.sleep(OFFLINE_TIMEOUT / 2)
            now = time.time()
            offline_devices = []
            with self.last_seen_lock:
                for device_id, ts in list(self.last_seen.items()):
                    if now - ts > OFFLINE_TIMEOUT:
                        offline_devices.append(device_id)
                        self.last_seen.pop(device_id, None)
            
            if not offline_devices: continue

            db = SessionLocal()
            try:
                for device_id in offline_devices:
                    dev = db.query(Device).filter(Device.ma_thiet_bi == device_id).first()
                    if dev and dev.trang_thai == "online":
                        dev.trang_thai = "offline"
                        db.commit()
                        logger.warning(f"[MQTT] Auto-set offline: {device_id}")
                        threading.Thread(target=process_device_offline_notification, args=(device_id,)).start()
            except Exception as e:
                db.rollback()
                logger.error(f"Error in auto-offline loop: {e}")
            finally:
                db.close()

    def start(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
            print(f"🚀 MQTT Handler started at {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            print(f"❌ MQTT start error: {e}")

mqtt_handler = MQTTHandler()
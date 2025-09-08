# rules/mqtt_handler.py
import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from database import SessionLocal
from rooms.models import Room
from devices.models import Device, DeviceField, Telemetry
from .models import Command
from .rule_engine import RuleEngine

# MQTT config
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT   = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER   = os.getenv("MQTT_USERNAME", "")
MQTT_PASS   = os.getenv("MQTT_PASSWORD", "")

# Offline timeout in seconds
OFFLINE_TIMEOUT = 10

class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        if MQTT_USER and MQTT_PASS:
            self.client.username_pw_set(MQTT_USER, MQTT_PASS)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connected = False
        self.rule_engine = RuleEngine()

        # Thread-safe dict để lưu last_seen timestamp của mỗi device
        self.last_seen: Dict[str, float] = {}
        self.last_seen_lock = threading.Lock()

        # Start auto-offline monitor
        threading.Thread(target=self._auto_offline_loop, daemon=True).start()

    # --- MQTT callbacks ---
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
        except Exception:
            print(f"⚠️ Bad JSON on {topic}: {msg.payload[:128]}")
            return

        if kind == "data":
            self._handle_data(ma_phong, payload)
        elif kind == "ack":
            self._handle_ack(payload)

    # --- Handle device data ---
    def _handle_data(self, ma_phong: str, data: Dict[str, Any]):
        """
        Payload kỳ vọng:
        {
          "device_id": "<sensor_id>",
          "data": {"temp": 32, "...": ...},
          "timestamp": 1712345678
        }
        """
        db = SessionLocal()
        try:
            device_id = data.get("device_id")
            sensor_data = data.get("data") or {}
            if not device_id or not sensor_data:
                print(f"⚠️ Missing device_id/data: {data}")
                return

            room = db.query(Room).filter(Room.ma_phong == ma_phong).first()
            if not room:
                print(f"❌ Room {ma_phong} not found")
                return

            dev = (
                db.query(Device)
                .filter(Device.ma_thiet_bi == device_id, Device.phong_id == room.id)
                .first()
            )
            if not dev:
                print(f"❌ Device {device_id} not in room {ma_phong}")
                return

            # --- Update device online status ---
            dev.last_seen = datetime.utcnow()
            dev.trang_thai = "online"

            with self.last_seen_lock:
                self.last_seen[device_id] = time.time()

            # --- Save telemetry ---
            for k, v in sensor_data.items():
                field = (
                    db.query(DeviceField)
                    .filter(DeviceField.thiet_bi_id == dev.id, DeviceField.khoa == k)
                    .first()
                )
                if not field:
                    continue
                db.add(Telemetry(
                    thiet_bi_id=dev.id, khoa=k, gia_tri=str(v), thoi_gian=datetime.utcnow()
                ))

            db.commit()

            # --- Evaluate rules ---
            self.rule_engine.evaluate_rules(
                db, room_id=room.id, device_id=device_id, sensor_data=sensor_data
            )
            print(f"✅ Data processed from {device_id}: {sensor_data}")

        except Exception as e:
            db.rollback()
            print(f"❌ handle_data error: {e}")
        finally:
            db.close()

    # --- Handle command ACK ---
    def _handle_ack(self, data: Dict[str, Any]):
        cmd_id = data.get("cmd_id")
        if not cmd_id:
            return
        db = SessionLocal()
        try:
            cmd = db.query(Command).filter(Command.id == cmd_id).first()
            if not cmd:
                print(f"⚠️ ACK for missing command {cmd_id}")
                return
            status = data.get("status", "unknown")
            if status == "ok":
                cmd.status = "acked"
                cmd.acked_at = datetime.utcnow()
            else:
                cmd.status = "failed"
                cmd.error_message = data.get("message", "Device error")
            db.commit()
            print(f"✅ Command {cmd_id} updated: {cmd.status}")
        except Exception as e:
            db.rollback()
            print(f"❌ handle_ack error: {e}")
        finally:
            db.close()

    # --- Auto-offline monitor ---
    def _auto_offline_loop(self):
        """Thread chạy background để set offline nếu không nhận message"""
        while True:
            now = time.time()
            offline_devices = []
            with self.last_seen_lock:
                for device_id, ts in list(self.last_seen.items()):
                    if now - ts > OFFLINE_TIMEOUT:
                        offline_devices.append(device_id)
                        self.last_seen.pop(device_id)
            # Update DB ngoài lock
            db = SessionLocal()
            try:
                for device_id in offline_devices:
                    dev = db.query(Device).filter(Device.ma_thiet_bi == device_id).first()
                    if dev:
                        dev.trang_thai = "offline"
                        dev.last_seen = datetime.utcnow()  # Cập nhật với thời gian hiện tại
                        db.commit()
                        print(f"[MQTT] Auto-set offline: {device_id}")
            except Exception:
                db.rollback()
            finally:
                db.close()
            time.sleep(1)

    # --- Start MQTT ---
    def start(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
            print(f"🚀 MQTT Handler started at {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            print(f"❌ MQTT start error: {e}")


# Singleton instance
mqtt_handler = MQTTHandler()

# --- Helper send command function ---
def send_command_to_device(
    command_id: int, device_id: str, command: str, payload: Optional[Dict[str, Any]] = None
) -> bool:
    """Publish lệnh đến topic iot/{ma_phong}/cmd/{device_id} và update trạng thái 'sent'."""
    db = SessionLocal()
    try:
        dev = db.query(Device).filter(Device.ma_thiet_bi == device_id).first()
        if not dev:
            print(f"❌ send_command: device {device_id} not found")
            return False
        room = db.query(Room).filter(Room.id == dev.phong_id).first()
        if not room:
            print(f"❌ send_command: room for device {device_id} not found")
            return False

        topic = f"iot/{room.ma_phong}/cmd/{device_id}"
        message = {
            "cmd_id": command_id,
            "command": command,
            "params": payload or {},
            "timestamp": int(datetime.utcnow().timestamp())
        }
        if not mqtt_handler.connected:
            print("❌ MQTT not connected")
            return False

        rc = mqtt_handler.client.publish(topic, json.dumps(message)).rc
        if rc == mqtt.MQTT_ERR_SUCCESS:
            cmd = db.query(Command).filter(Command.id == command_id).first()
            if cmd:
                cmd.status = "sent"
                cmd.sent_at = datetime.utcnow()
                db.commit()
            print(f"⚡ MQTT → {topic}: {message}")
            return True
        print(f"❌ MQTT publish rc={rc}")
        return False
    except Exception as e:
        db.rollback()
        print(f"❌ send_command error: {e}")
        return False
    finally:
        db.close()

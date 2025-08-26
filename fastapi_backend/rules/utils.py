# rules/utils.py
import json
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from database import SessionLocal
from rooms.models import Room
from devices.models import Device
from .models import Command

# mqtt_handler sẽ set biến này khi start
mqtt_client = None  

def send_command_to_device(command_id: int, device_id: str, command: str, payload: Optional[Dict[str, Any]] = None) -> bool:
    """Publish lệnh đến device qua MQTT"""
    from .mqtt_handler import mqtt_handler  # import tại runtime tránh vòng lặp

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

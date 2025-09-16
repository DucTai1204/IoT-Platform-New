#!/usr/bin/env python3
"""
Script test tính năng phát hiện device offline/online và gửi thông báo Telegram
"""

import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# MQTT config
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
DEVICE_ID = "test-device-001"
ROOM_CODE = "phong-test"

def on_connect(client, userdata, flags, rc):
    print(f"✅ MQTT Connected: {rc}")
    client.subscribe(f"iot/{ROOM_CODE}/data")

def on_message(client, userdata, msg):
    print(f"📨 Received: {msg.topic} -> {msg.payload.decode()}")

def send_test_data(client, device_id, room_code, temperature=25.0, humidity=60.0):
    """Gửi dữ liệu test từ device"""
    data = {
        "device_id": device_id,
        "timestamp": time.time(),
        "data": {
            "temperature": temperature,
            "humidity": humidity
        }
    }
    
    topic = f"iot/{room_code}/data"
    message = json.dumps(data)
    
    result = client.publish(topic, message)
    print(f"📤 Sent to {topic}: {message}")
    return result.rc == 0

def main():
    print("🧪 Test Device Offline/Online Detection")
    print("=" * 50)
    
    # Tạo MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Kết nối MQTT
        print(f"🔌 Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Chờ kết nối
        time.sleep(2)
        
        print(f"\n📱 Testing device: {DEVICE_ID} in room: {ROOM_CODE}")
        print("📋 Test plan:")
        print("1. Gửi dữ liệu liên tục (device online)")
        print("2. Dừng gửi dữ liệu (device sẽ offline sau 10 giây)")
        print("3. Gửi lại dữ liệu (device online trở lại)")
        print("\n⏰ Bắt đầu test...")
        
        # Phase 1: Gửi dữ liệu liên tục (device online)
        print(f"\n🟢 Phase 1: Device online - gửi dữ liệu liên tục")
        for i in range(5):
            temp = 25.0 + i * 0.5
            humi = 60.0 + i * 1.0
            send_test_data(client, DEVICE_ID, ROOM_CODE, temp, humi)
            time.sleep(2)
        
        # Phase 2: Dừng gửi dữ liệu (device sẽ offline)
        print(f"\n🔴 Phase 2: Dừng gửi dữ liệu - device sẽ offline sau 10 giây")
        print("⏳ Chờ 12 giây để device offline...")
        time.sleep(12)
        
        # Phase 3: Gửi lại dữ liệu (device online trở lại)
        print(f"\n🟢 Phase 3: Gửi lại dữ liệu - device online trở lại")
        send_test_data(client, DEVICE_ID, ROOM_CODE, 30.0, 70.0)
        
        print(f"\n✅ Test hoàn thành!")
        print("📱 Kiểm tra Telegram để xem thông báo:")
        print("   - Device offline (sau 10 giây không nhận dữ liệu)")
        print("   - Device online (khi gửi lại dữ liệu)")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 MQTT disconnected")

if __name__ == "__main__":
    main()

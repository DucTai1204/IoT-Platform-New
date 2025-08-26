import time
import json
import random
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MA_PHONG = "52725f4dc39547ef9c7342d5537730f6"  # Mã phòng hợp lệ

# Danh sách thiết bị và field hợp lệ
devices = [
    {
        "ma_thiet_bi": "nothing",  # Thiết bị 1
        "fields": ["temperature", "humidity", "status"]
    },
    {
        "ma_thiet_bi": "3a5d1102609343a7b7c471aeb86a2e6a",  # Thiết bị 2
        "fields": ["nhietdo", "doam", "thoigian"]
    }
]

TOPIC = f"iot/{MA_PHONG}/data"

# Kết nối MQTT
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

count = 0
while True:
    count += 1

    for dev in devices:
        if dev["ma_thiet_bi"] == "nothing":
            # Sinh dữ liệu cho thiết bị 1
            payload = {
                "ma_thiet_bi": dev["ma_thiet_bi"],
                "temperature": round(random.uniform(24.0, 30.0), 2),
                "humidity": round(random.uniform(50.0, 65.0), 2),
                "status": random.choice([True, False]),
                "timestamp": time.time()
            }

        elif dev["ma_thiet_bi"] == "3a5d1102609343a7b7c471aeb86a2e6a":
            # Sinh dữ liệu cho thiết bị 2
            payload = {
                "ma_thiet_bi": dev["ma_thiet_bi"],
                "nhietdo": round(random.uniform(24.0, 30.0), 2),
                "doam": round(random.uniform(50.0, 65.0), 2),
                "thoigian": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time()
            }

        client.publish(TOPIC, json.dumps(payload))
        print(f"✅ Published to {TOPIC}: {payload}")

    time.sleep(10)

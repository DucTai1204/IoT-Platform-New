import time, json, random
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "127.0.0.1"
PORT   = 1883
ROOM   = "13edc6c57df2421fbbc4c5f8265ccb9f"
DEVICE_ID = "09d392dae81244fe831693055290eeee"

client = mqtt.Client()

def publish_multi_data():
    while True:
        payload = {
            "device_id": DEVICE_ID,
            "data": {
                "temp": random.randint(20, 40),
                "hum": random.randint(30, 80),
                "time": int(time.time())
            },
            "timestamp": int(time.time())
        }
        topic = f"iot/{ROOM}/data"
        client.publish(topic, json.dumps(payload))
        print(f"📡 MULTI {DEVICE_ID} → {topic}: {payload}")
        time.sleep(5)

client.connect(BROKER, PORT, 60)
publish_multi_data()

import time, json, random
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "127.0.0.1"
PORT   = 1883
ROOM   = "13edc6c57df2421fbbc4c5f8265ccb9f"
DEVICE_ID = "b6c203a59ed04a40b2f4741e17e3a3ea"

client = mqtt.Client()

def publish_sensor_data():
    while True:
        payload = {
            "device_id": DEVICE_ID,
            "data": {
                "temp": random.randint(20, 35),
                "hum": random.randint(40, 80),
            },
            "timestamp": int(time.time())
        }
        topic = f"iot/{ROOM}/data"
        client.publish(topic, json.dumps(payload))
        print(f"📡 SENSOR {DEVICE_ID} → {topic}: {payload}")
        time.sleep(5)

client.connect(BROKER, PORT, 60)
publish_sensor_data()

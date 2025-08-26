# simulator/dht11.py
import time
import random
import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

ROOM_CODE = "13edc6c57df2421fbbc4c5f8265ccb9f"   # mã phòng, khớp với DB
DEVICE_ID = "b6c203a59ed04a40b2f4741e17e3a3ea"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

try:
    while True:
        temp = random.randint(25, 36)  # giả lập nhiệt độ
        payload = {
            "device_id": DEVICE_ID,
            "data": {"temp": temp}
        }
        topic = f"iot/{ROOM_CODE}/data"
        client.publish(topic, json.dumps(payload))
        print(f"🌡️ Sensor gửi → {topic}: {payload}")
        time.sleep(3)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()

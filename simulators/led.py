# simulator/led.py
import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

ROOM_CODE = "13edc6c57df2421fbbc4c5f8265ccb9f"   # mã phòng, khớp với DB
DEVICE_ID = "b04490f4f52f4094900d95a30c9719f1"

TOPIC_CMD = f"iot/{ROOM_CODE}/cmd/{DEVICE_ID}"

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    command = payload.get("command")
    print(f"⚡ Device {DEVICE_ID} nhận lệnh: {command}, payload={payload}")

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(TOPIC_CMD)
print(f"📡 Device {DEVICE_ID} đang lắng nghe {TOPIC_CMD}...")

client.loop_forever()

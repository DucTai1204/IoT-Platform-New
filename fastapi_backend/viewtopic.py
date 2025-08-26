import os
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = "iot/d1eea3db879547dbaa4f0ce55db08cb5/data"  # thay <ma_phong> bằng mã phòng thật

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT with result code {rc}")
    client.subscribe(TOPIC)
    print(f"📡 Subscribed to topic: {TOPIC}")

def on_message(client, userdata, msg):
    print(f"📥 Message received on {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"🔌 Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("⏹ Stopped.")

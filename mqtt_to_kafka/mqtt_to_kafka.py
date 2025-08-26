import os
import json
import time
import signal
import sys
import requests
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from functools import lru_cache

# ===== CONFIG =====
MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = "iot/+/data"

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iot-events")

ROOM_API_BASE = os.getenv("ROOM_API_BASE", "http://127.0.0.1:8000")
print(ROOM_API_BASE)

# ===== Kafka Producer =====
print(f"🔌 Kafka broker: {KAFKA_BROKER}")
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=3,
    acks='all'
)

# ===== Cache danh sách thiết bị + field hợp lệ =====
@lru_cache(maxsize=100)
def get_valid_devices_and_fields(ma_phong):
    try:
        url = f"{ROOM_API_BASE}/rooms/internal/rooms/{ma_phong}/fields"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            return {dev["ma_thiet_bi"]: {f["khoa"] for f in dev["fields"]} for dev in data}
        else:
            print(f"⚠️ Room {ma_phong} not found via API")
            return {}
    except Exception as e:
        print(f"❌ Error fetching devices for {ma_phong}: {e}")
        return {}

# ===== MQTT Callbacks =====
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ MQTT connected with result code {rc}")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"❌ MQTT connect failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        parts = msg.topic.split("/")
        if len(parts) < 3:
            print("⚠️ Invalid topic format")
            return

        ma_phong = parts[1]

        # Lấy mapping thiết bị -> field hợp lệ
        valid_map = get_valid_devices_and_fields(ma_phong)
        if not valid_map:
            print(f"⛔ No valid devices for room {ma_phong}")
            return

        ma_thiet_bi = payload.get("ma_thiet_bi")
        if not ma_thiet_bi:
            print("⚠️ Missing 'ma_thiet_bi' in payload")
            return

        if ma_thiet_bi not in valid_map:
            print(f"⛔ Device '{ma_thiet_bi}' not in room {ma_phong}")
            return

        # Kiểm tra field trong payload (bỏ qua ma_thiet_bi và timestamp)
        for key in payload.keys():
            if key in ("ma_thiet_bi", "timestamp"):
                continue
            if key not in valid_map[ma_thiet_bi]:
                print(f"⛔ Field '{key}' not allowed for device {ma_thiet_bi} in room {ma_phong}")
                return

        # Gửi Kafka nếu hợp lệ
        future = producer.send(KAFKA_TOPIC, value={
            "ma_phong": ma_phong,
            "data": payload
        })
        result = future.get(timeout=5)
        producer.flush()
        print(f"📤 Sent to Kafka topic '{KAFKA_TOPIC}' at offset {result.offset}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")

# ===== MQTT Client =====
print(f"🔌 MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# ===== Signal Handler =====
def signal_handler(sig, frame):
    print("\n🛑 Stopping MQTT-Kafka bridge...")
    client.loop_stop()
    client.disconnect()
    producer.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("🚀 MQTT to Kafka bridge running...")
while True:
    time.sleep(1)

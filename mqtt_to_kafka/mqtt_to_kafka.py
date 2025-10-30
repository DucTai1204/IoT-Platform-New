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
# Thay đổi giá trị mặc định để phù hợp với tên service trong Docker Compose
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
#MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = "iot/+/data"

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:29092")
# KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "iot-events")

ROOM_API_BASE = os.getenv("ROOM_API_BASE", "127.0.0.1:8000")
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
        # Thêm http:// hoặc https:// vào URL để requests hoạt động đúng
        url = f"{ROOM_API_BASE}/rooms/internal/rooms/{ma_phong}/fields"
        print(f"🔍 Fetching from API: {url}")
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            data = r.json()
            return {dev["ma_thiet_bi"]: {f["khoa"] for f in dev["fields"]} for dev in data}
        else:
            print(f"⚠️ Room {ma_phong} not found via API, status code: {r.status_code}")
            return {}
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to FastAPI backend: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error fetching devices for {ma_phong}: {e}")
        return {}

# ===== MQTT Callbacks =====
def on_connect(client, userdata, flags, rc,properties=None):
    if rc == 0:
        print(f"✅ MQTT connected with result code {rc}")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"❌ MQTT connect failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        print(f"📥 Received message on topic: {msg.topic}")
        payload = json.loads(msg.payload.decode())

        parts = msg.topic.split("/")
        if len(parts) < 3:
            print("⚠️ Invalid topic format")
            return

        ma_phong = parts[1]
        print(f"Processing data for room: {ma_phong}")

        # Tạo Kafka topic động theo maphong
        kafka_topic_for_room = f"iot.{ma_phong}.data"

        # Gửi payload vào Kafka topic riêng cho room
        future = producer.send(kafka_topic_for_room, value=payload)
        result = future.get(timeout=5)
        producer.flush()
        print(f"📤 Sent to Kafka topic '{kafka_topic_for_room}' at offset {result.offset}")

    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON payload")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

# ===== MQTT Client =====
print(f"🔌 MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
# client = mqtt.Client(protocol=mqtt.MQTTv311)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
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
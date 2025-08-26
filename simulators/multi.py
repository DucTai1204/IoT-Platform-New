import json
import time
import random
import threading
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

ROOM_CODE = "13edc6c57df2421fbbc4c5f8265ccb9f"   # mã phòng, khớp DB
DEVICE_ID = "b6c203a59ed04a40b2f4741e17e3a3ea"   # đổi id cho mỗi node

TOPIC_DATA = f"iot/{ROOM_CODE}/data"
TOPIC_CMD = f"iot/{ROOM_CODE}/cmd/{DEVICE_ID}"
TOPIC_STATUS = f"iot/{ROOM_CODE}/status/{DEVICE_ID}"

# ==== Xử lý khi nhận lệnh ====
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    command = payload.get("command")
    print(f"⚡ {DEVICE_ID} nhận lệnh: {command}, payload={payload}")

    # phản hồi trạng thái
    status_payload = {"device_id": DEVICE_ID, "status": f"executed {command}", "ts": time.time()}
    client.publish(TOPIC_STATUS, json.dumps(status_payload))
    print(f"📤 {DEVICE_ID} gửi trạng thái → {TOPIC_STATUS}: {status_payload}")

# ==== Khởi tạo MQTT ====
client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(TOPIC_CMD)
print(f"📡 {DEVICE_ID} đang lắng nghe {TOPIC_CMD}...")

# ==== Thread giả lập gửi dữ liệu cảm biến ====
def send_data():
    while True:
        temp = random.randint(25, 36)
        payload = {"device_id": DEVICE_ID, "data": {"temp": temp}}
        client.publish(TOPIC_DATA, json.dumps(payload))
        print(f"🌡️ {DEVICE_ID} gửi dữ liệu → {TOPIC_DATA}: {payload}")
        time.sleep(5)

threading.Thread(target=send_data, daemon=True).start()

# ==== Loop chính ====
client.loop_forever()

import paho.mqtt.client as mqtt
import json
import time

BROKER = "192.168.0.197"
# BROKER ="localhost"
PORT = 1883
ROOM = "13edc6c57df2421fbbc4c5f8265ccb9f"
DEVICE_ID = "b04490f4f52f4094900d95a30c9719f1"

# trạng thái LED (giả lập)
led_state = "off"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to broker")
        topic = f"iot/{ROOM}/cmd/{DEVICE_ID}"
        client.subscribe(topic)
        print(f"🔔 ACTUATOR {DEVICE_ID} subscribed {topic}")
    else:
        print(f"❌ Connect failed: {rc}")

def on_message(client, userdata, msg):
    global led_state
    try:
        payload = json.loads(msg.payload.decode())
        print(f"💡 ACTUATOR {DEVICE_ID} nhận lệnh: {payload}")

        cmd_id = payload.get("cmd_id")
        command = payload.get("command")

        if command == "turn_on":
            led_state = "on"
            print("✨ LED đã BẬT (giả lập sáng)")
        elif command == "turn_off":
            led_state = "off"
            print("🌑 LED đã TẮT (giả lập tắt)")
        else:
            print("⚠️ Lệnh không hỗ trợ")

        # gửi ACK về server
        ack_topic = f"iot/{ROOM}/ack"
        ack_payload = {
            "cmd_id": cmd_id,
            "status": "ok",
            "message": f"{DEVICE_ID} executed {command}, state={led_state}"
        }
        client.publish(ack_topic, json.dumps(ack_payload))
        print(f"✅ ACK gửi về {ack_topic}: {ack_payload}")

    except Exception as e:
        print(f"❌ Error on message: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

# vòng lặp giả lập LED có thể phát telemetry trạng thái lên server
try:
    while True:
        telemetry = {
            "device_id": DEVICE_ID,
            "data": {"led_state": led_state},
            "timestamp": int(time.time())
        }
        topic = f"iot/{ROOM}/data"
        client.publish(topic, json.dumps(telemetry))
        print(f"📤 Gửi telemetry: {telemetry}")
        time.sleep(10)  # mỗi 10s gửi trạng thái LED
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()

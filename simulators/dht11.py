import time
import json
import random
import paho.mqtt.client as mqtt

# --- Cấu hình ---
BROKER = "192.168.69.159"
# BROKER = "127.0.0.1"
PORT  = 1883
ROOM  = "13edc6c57df2421fbbc4c5f8265ccb9f"
DEVICE_ID = "b6c203a59ed04a40b2f4741e17e3a3ea"

# Khởi tạo client với API v2 để tránh cảnh báo (warning)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def publish_sensor_data():
    """
    Vòng lặp vô hạn để tạo và gửi dữ liệu cảm biến.
    """
    while True:
        # 1. Gom dữ liệu sensor vào một dictionary con
        sensor_values = {
            "temp": random.randint(20, 35),
            "hum": random.randint(40, 80)
        }

        # 2. Tạo payload với cấu trúc lồng nhau đúng như server mong muốn
        payload = {
            "device_id": DEVICE_ID,    # <-- Key phải là "device_id"
            "data": sensor_values      # <-- Dữ liệu sensor nằm trong key "data"
        }
        
        topic = f"iot/{ROOM}/data"
        
        # Chuyển dictionary thành chuỗi JSON và gửi đi
        client.publish(topic, json.dumps(payload))
        
        print(f"📡 SENSOR {DEVICE_ID} → {topic}: {payload}")
        time.sleep(5)

# --- Chạy chương trình ---
try:
    print("Connecting to MQTT Broker...")
    client.connect(BROKER, PORT, 60)
    
    # Bắt đầu một luồng riêng để xử lý mạng cho MQTT (cách làm tốt nhất)
    client.loop_start() 
    
    # Bắt đầu gửi dữ liệu
    publish_sensor_data()

except KeyboardInterrupt:
    print("\nScript stopped by user.")
    client.loop_stop()
    client.disconnect()
except Exception as e:
    print(f"An error occurred: {e}")
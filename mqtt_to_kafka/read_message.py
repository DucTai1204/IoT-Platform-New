import paho.mqtt.client as mqtt
from kafka import KafkaProducer
import json
import logging
import os

# --- Cấu hình ---
# Lấy thông tin từ biến môi trường, nếu không có thì dùng giá trị mặc định
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_SUBSCRIBE = "iot/+/data" 

# Khi chạy trong Docker, dùng tên service 'kafka'. Khi chạy local, dùng 'localhost'.
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Khởi tạo Kafka Producer ---
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        # Serializer này tự động chuyển dictionary Python thành chuỗi JSON chuẩn (dùng nháy kép)
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        # Thêm cấu hình để producer tự thử lại nếu broker tạm thời không sẵn sàng
        retries=5
    )
    logging.info(f"✅ Đã kết nối thành công đến Kafka Broker tại {KAFKA_BROKER}!")
except Exception as e:
    logging.error(f"❌ Không thể kết nối đến Kafka Broker: {e}")
    exit(1)

# --- Các hàm callback của MQTT ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info(f"✅ Đã kết nối thành công đến MQTT Broker tại {MQTT_BROKER}!")
        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
        logging.info(f"👂 Đang lắng nghe MQTT trên topic: {MQTT_TOPIC_SUBSCRIBE}")
    else:
        logging.error(f"❌ Kết nối MQTT thất bại, mã lỗi: {rc}")

def on_message(client, userdata, msg):
    """
    Hàm được gọi mỗi khi có tin nhắn từ MQTT.
    Nhiệm vụ: Chuyển tiếp tin nhắn sang Kafka với tên topic tương ứng.
    """
    try:
        logging.info(f"📬 MQTT Received | Topic: {msg.topic}")
        
        # 1. Chuyển đổi tên topic MQTT thành tên topic Kafka
        # Ví dụ: "iot/phong-A/data" -> "iot.phong-A.data"
        kafka_topic_name = msg.topic.replace('/', '.')
        
        # 2. Decode payload từ MQTT (dạng bytes) thành dictionary Python
        # Đây là bước quan trọng để đảm bảo payload là JSON
        payload_dict = json.loads(msg.payload.decode('utf-8'))
        
        # 3. Gửi dictionary vào Kafka. Producer sẽ tự động serialize nó.
        producer.send(kafka_topic_name, value=payload_dict)
        
        logging.info(f"✈️ Sent to Kafka | Topic: {kafka_topic_name} | Value: {payload_dict}")

    except json.JSONDecodeError:
        logging.warning(f"⚠️ Tin nhắn trên topic {msg.topic} không phải là JSON hợp lệ, bỏ qua: {msg.payload}")
    except Exception as e:
        logging.error(f"Lỗi khi xử lý tin nhắn hoặc gửi đến Kafka: {e}")

# --- Khởi tạo và chạy MQTT Client ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    logging.info("\n🛑 Đang dừng chương trình...")
except Exception as e:
    logging.error(f"Lỗi kết nối MQTT ban đầu: {e}")
finally:
    if producer:
        producer.flush()
        producer.close()
        logging.info("Đã đóng kết nối Kafka.")
    mqtt_client.disconnect()
    logging.info("Đã ngắt kết nối MQTT.")
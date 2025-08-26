import pymongo
import time
from datetime import datetime
from telegram_notifier import send_telegram_alert
from email_notifier import send_email_alert

# Kết nối MongoDB
client = pymongo.MongoClient("mongodb://tai:mk_tai@localhost:27017/?authSource=iot")
collection = client.iot.real

# Ngưỡng cảnh báo
TEMP_THRESHOLD = 35.0
HUMI_THRESHOLD = 30.0

# Tránh gửi cảnh báo trùng
alerted_ids = set()

def monitor_abnormal_data():
    print("🚦 Đang giám sát MongoDB để phát hiện dữ liệu bất thường...")

    while True:
        try:
            latest_doc = collection.find_one(sort=[("processed_at", -1)])
            if latest_doc:
                _id = str(latest_doc["_id"])
                temp = latest_doc.get("temperature", 0)
                humi = latest_doc.get("humidity", 0)
                device_id = latest_doc.get("device_id", "Unknown")
                ts = latest_doc.get("timestamp", time.time())

                if _id in alerted_ids:
                    time.sleep(2)
                    continue

                if temp > TEMP_THRESHOLD or humi < HUMI_THRESHOLD:
                    ts_str = datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
                    msg = (
                        f"🚨 CẢNH BÁO!\n"
                        f"🆔 Thiết bị: {device_id}\n"
                        f"🌡️ Nhiệt độ: {temp}°C\n"
                        f"💧 Độ ẩm: {humi}%\n"
                        f"🕐 Thời gian: {ts_str}"
                    )

                    # Gửi cả 2 kênh
                    send_telegram_alert(msg)
                    send_email_alert(msg)

                    alerted_ids.add(_id)
                else:
                    print(f"✅ OK | {device_id} | {temp}°C | {humi}%")

            time.sleep(2)

        except Exception as e:
            print(f"❌ Lỗi giám sát: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_abnormal_data()

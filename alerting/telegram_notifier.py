import requests

TELEGRAM_BOT_TOKEN = "7368288364:AAGXS9rV523NmOpKLYVIhS02pgQRoRSryr0"
CHAT_ID = 5606024020

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("📨 Telegram đã gửi thành công.")
        else:
            print(f"❌ Telegram lỗi: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi Telegram: {e}")

# telegram_notifier.py
import os
import json
import requests
from typing import Optional

def get_telegram_config():
    """Lấy cấu hình Telegram từ file hoặc environment variables"""
    try:
        # Thử đọc từ file config trước
        if os.path.exists("telegram_config.json"):
            with open("telegram_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("bot_token"), config.get("chat_id"), config.get("enable_notifications", True)
        
        # Fallback về environment variables
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "7368288364:AAGXS9rV523NmOpKLYVIhS02pgQRoRSryr0")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "5606024020")
        return bot_token, chat_id, True
        
    except Exception as e:
        print(f"⚠️ Lỗi đọc cấu hình Telegram: {e}")
        # Fallback về default values
        return "7368288364:AAGXS9rV523NmOpKLYVIhS02pgQRoRSryr0", "5606024020", True

def send_telegram_alert(message: str) -> bool:
    """
    Gửi thông báo qua Telegram
    
    Args:
        message: Nội dung thông báo
        
    Returns:
        bool: True nếu gửi thành công, False nếu thất bại
    """
    bot_token, chat_id, enabled = get_telegram_config()
    
    if not enabled:
        print("⚠️ Thông báo Telegram đã bị tắt")
        return False
        
    if not bot_token or not chat_id:
        print("⚠️ Telegram bot token hoặc chat ID chưa được cấu hình")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("📨 Telegram đã gửi thành công.")
            return True
        else:
            print(f"❌ Telegram lỗi: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Lỗi Telegram: {e}")
        return False

def send_device_offline_alert(device_id: str, device_name: str, room_name: str, last_seen: str) -> bool:
    """
    Gửi thông báo khi device offline
    
    Args:
        device_id: ID của device
        device_name: Tên device
        room_name: Tên phòng
        last_seen: Thời gian cuối cùng device online
        
    Returns:
        bool: True nếu gửi thành công
    """
    message = (
        f"🔴 <b>THIẾT BỊ OFFLINE</b>\n\n"
        f"🆔 <b>Thiết bị:</b> {device_name} ({device_id})\n"
        f"🏠 <b>Phòng:</b> {room_name}\n"
        f"⏰ <b>Lần cuối online:</b> {last_seen}\n"
        f"📡 <b>Trạng thái:</b> Mất kết nối"
    )
    
    return send_telegram_alert(message)

def send_device_online_alert(device_id: str, device_name: str, room_name: str) -> bool:
    """
    Gửi thông báo khi device online trở lại
    
    Args:
        device_id: ID của device
        device_name: Tên device
        room_name: Tên phòng
        
    Returns:
        bool: True nếu gửi thành công
    """
    message = (
        f"🟢 <b>THIẾT BỊ ONLINE</b>\n\n"
        f"🆔 <b>Thiết bị:</b> {device_name} ({device_id})\n"
        f"🏠 <b>Phòng:</b> {room_name}\n"
        f"📡 <b>Trạng thái:</b> Đã kết nối lại"
    )
    
    return send_telegram_alert(message)

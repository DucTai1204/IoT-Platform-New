import os
import requests
import logging

logger = logging.getLogger(__name__)

def send_telegram_alert(message: str, chat_id: str) -> bool:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.warning("Missing TELEGRAM_BOT_TOKEN. Cannot send Telegram alert.")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": message, 
        "parse_mode": "HTML"
    }

    logger.info(f"Attempting to send Telegram message with payload: {payload}")

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() # Ném lỗi nếu status code là 4xx hoặc 5xx
        
        if response.json().get("ok"):
            logger.info(f"✅ Telegram message sent successfully to chat_id: {chat_id}")
            return True
        else:
            logger.error(f"❌ Telegram API error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Telegram request exception: {e}")
        return False
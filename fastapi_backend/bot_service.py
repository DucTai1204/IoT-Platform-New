import asyncio
import logging
import threading
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from redis_client import redis_client # <<< 1. Import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_service")

# Lấy token từ biến môi trường
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    token = f"TOKEN-{user_id}"
    
    # <<< 2. Sửa logic: Lưu token vào Redis thay vì dictionary >>>
    # Dùng token làm key, user_id (chat_id) làm value
    # ex=600 nghĩa là token sẽ tự động hết hạn sau 600 giây (10 phút)
    redis_client.set(token, user_id, ex=600)
    
    await update.message.reply_text(
        f"Xin chào {update.effective_user.first_name}!\n"
        f"🔑 Token của bạn là: {token}\n"
        f"Token này có hiệu lực trong 10 phút."
    )

def run_bot():
    logger.info("▶️ Telegram bot thread started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("🚀 Telegram bot service started")
    app.run_polling()

def start_bot_in_thread():
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
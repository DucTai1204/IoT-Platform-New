import os
import redis
from dotenv import load_dotenv

# Đảm bảo các biến môi trường được nạp
load_dotenv()
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    # host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True 
)

# Kiểm tra kết nối khi khởi động
try:
    redis_client.ping()
    print("✅ Connected to Redis successfully.")
except redis.exceptions.ConnectionError as e:
    print(f"❌ Could not connect to Redis: {e}")
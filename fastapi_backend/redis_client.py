import os
import redis
from dotenv import load_dotenv

# Đảm bảo các biến môi trường được nạp
load_dotenv()

# Tạo một client duy nhất để kết nối đến Redis
# decode_responses=True giúp kết quả trả về từ Redis là string, không phải bytes
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
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
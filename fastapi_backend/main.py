# main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
import logging
load_dotenv()

logging.getLogger("telegram.ext").setLevel(logging.WARNING)
logging.getLogger("telegram.bot").setLevel(logging.WARNING)

# Tắt log INFO của thư viện httpx (ví dụ: "HTTP Request: POST...")
logging.getLogger("httpx").setLevel(logging.WARNING)

# Routers
from auth.routes import router as auth_router
from rooms.routes import router as rooms_router
from devices.routes import router as device_router
from rules.routes import router as rule_router
from notifications.routes import router as notifications_router
from mongo.routes import router as mongo_router
# <<< SỬA DÒNG IMPORT TẠI ĐÂY >>>
# Bỏ `user_tokens` ra khỏi dòng import vì nó không còn tồn tại
from bot_service import start_bot_in_thread

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code chạy lúc startup
    try:
        from rules.mqtt_handler import mqtt_handler
        mqtt_handler.start()
        print("🚀 IoT Platform started with MQTT support")

        start_bot_in_thread()
        print("🚀 Telegram bot service started")
        
        print("🚀 IoT Platform started successfully")
        yield
    finally:
        # Code chạy lúc shutdown
        print("🛑 IoT Platform stopped gracefully")

app = FastAPI(
    title="IoT Platform API",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan 
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rooms_router, prefix="/rooms", tags=["Phòng"])
app.include_router(device_router, prefix="/devices", tags=["Thiết bị"])
app.include_router(rule_router)
app.include_router(notifications_router)
app.include_router(mongo_router, prefix="/mongo")
# Health check
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": "IoT Platform API is running"}


@app.get("/api/health", tags=["Health"])
def api_health_check():
    from rules.mqtt_handler import mqtt_handler

    return {
        "status": "healthy",
        "api_version": "v1",
        "features": ["auth", "rooms", "devices", "rules", "mqtt", "telegram", "redis"],
        "services": {
            "mqtt": {
                "status": "connected" if mqtt_handler.connected else "disconnected",
                "broker": f"{mqtt_handler.client._host}:{mqtt_handler.client._port}"
            },
            "telegram": {
                "status": "configured",
                "notifications": "enabled",
                # <<< SỬA TẠI ĐÂY: Xóa dòng `active_tokens` vì user_tokens không còn >>>
            }
        }
    }


# Run
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("RELOAD", "false").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload_flag)
#main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load .env
load_dotenv()

# Routers
from auth.routes import router as auth_router
from rooms.routes import router as rooms_router
from devices.routes import router as device_router
from rules.routes import router as rule_router

app = FastAPI(
    title="IoT Platform API",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}  # Ẩn phần Schemas trong Swagger
)

# CORS (chấp nhận tất cả origin)
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
app.include_router(rule_router)  # /rules, /commands

# Startup MQTT handler
@app.on_event("startup")
async def startup_event():
    try:
        from rules.mqtt_handler import mqtt_handler
        mqtt_handler.start()
        print("🚀 IoT Platform started with MQTT support")
    except Exception as e:
        print(f"⚠️ Failed to start MQTT handler: {e}")

# Health check
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": "IoT Platform API is running"}

@app.get("/api/health", tags=["Health"])
def api_health_check():
    return {
        "status": "healthy",
        "api_version": "v1",
        "features": ["auth", "rooms", "devices", "rules", "mqtt"]
    }

# Run
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("RELOAD", "false").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload_flag)

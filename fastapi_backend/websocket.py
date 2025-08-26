from fastapi import WebSocket, WebSocketDisconnect
from database import get_mongo
import asyncio

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        mongo = get_mongo()
        while True:
            try:
                latest = mongo["events"].find({}, {"_id": 0}).sort("timestamp", -1).limit(1)
                found = False
                for doc in latest:
                    found = True
                    await websocket.send_json(doc)
                    print("✅ Sent doc:", doc)
                if not found:
                    # Dummy data
                    await websocket.send_json({"info": "no recent data"})
                    print("📭 No data, sent dummy ping")
            except Exception as e:
                print("❌ Mongo query/send error:", e)
                await websocket.send_json({"error": str(e)})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print("❌ WebSocket main loop crashed:", e)

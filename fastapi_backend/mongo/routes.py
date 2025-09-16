from fastapi import APIRouter, Query
from pymongo import MongoClient
import os

router = APIRouter()

# Kết nối MongoDB (đọc từ ENV hoặc dùng default)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "iot_db")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]


@router.get("/mongo/query", tags=["MongoDB"])
def query_collection(
    collection: str = Query(..., description="Tên collection cần query")
):
    """
    Truyền tên collection để lấy toàn bộ document.
    """
    if collection not in db.list_collection_names():
        return {"error": f"Collection '{collection}' không tồn tại trong DB {MONGO_DB}"}

    data = list(db[collection].find({}, {"_id": 0}))  # bỏ _id cho dễ đọc JSON
    return {
        "collection": collection,
        "count": len(data),
        "documents": data
    }

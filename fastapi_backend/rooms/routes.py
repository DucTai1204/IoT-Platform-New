# rooms/routes.py
import os
import uuid
import threading
import paho.mqtt.client as mqtt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from database import get_db
from auth.security import get_current_user
from auth.models import NguoiDung
from .models import Room
from devices.models import Device, DeviceField
from .schemas import RoomCreate, RoomUpdate, RoomOut

# MQTT config
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

router = APIRouter()

# ==== MQTT BACKGROUND CLIENT ====
mqtt_client = mqtt.Client()

def mqtt_connect():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT connected to broker")
        else:
            print(f"❌ MQTT connection failed: {rc}")

    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Chạy loop_forever trong thread riêng để giữ kết nối
    thread = threading.Thread(target=mqtt_client.loop_forever, daemon=True)
    thread.start()

# # Gọi kết nối MQTT khi load file
mqtt_connect()

def mqtt_subscribe(topic: str):
    """Sub vào MQTT topic và giữ kết nối."""
    try:
        mqtt_client.subscribe(topic)
        print(f"✅ Subscribed to MQTT topic: {topic}")
    except Exception as e:
        print(f"❌ MQTT subscribe error: {e}")

# ==== API ====

@router.post(
    "/tao-phong",
    summary="Tạo phòng",
    description="Tạo một phòng mới và tự sub vào topic MQTT",
    response_model=RoomOut,
    status_code=status.HTTP_201_CREATED
)
def create_room(
    body: RoomCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    # Sinh ma_phong unique
    generated_code = uuid.uuid4().hex

    room = Room(
        ten_phong=body.ten_phong,
        mo_ta=body.mo_ta,
        vi_tri=body.vi_tri,
        nguoi_quan_ly_id=current_user.id,
        ma_phong=generated_code
    )
    db.add(room)
    db.commit()
    db.refresh(room)

    # Sub vào topic của phòng
    mqtt_subscribe(f"iot/{room.ma_phong}/data")

    return room

@router.get(
    "/",
    summary="Lấy danh sách phòng",
    description="Lấy danh sách tất cả các phòng của user hiện tại",
    response_model=List[RoomOut]
)
def list_rooms(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    rooms = (
        db.query(Room)
        .filter(Room.nguoi_quan_ly_id == current_user.id)
        .options(joinedload(Room.devices))
        .order_by(Room.id.desc())
        .all()
    )
    return rooms

@router.get(
    "/{room_id}",
    response_model=RoomOut,
    summary="Xem chi tiết phòng",
    description="API này dùng để lấy thông tin chi tiết của một phòng theo ID."
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    room = (
        db.query(Room)
        .options(joinedload(Room.devices))
        .filter(Room.id == room_id, Room.nguoi_quan_ly_id == current_user.id)
        .first()
    )
    if not room:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    return room
# @router.get("/rooms/{ma_phong}/fields")
# def get_room_devices_and_fields(ma_phong: str, db: Session = Depends(get_db)):
#     # Lấy phòng theo mã
#     room = db.query(Room).filter(Room.ma_phong == ma_phong).first()
#     if not room:
#         raise HTTPException(status_code=404, detail="Phòng không tồn tại")

#     # Lấy tất cả thiết bị trong phòng
#     devices = db.query(Device).filter(Device.phong_id == room.id).all()
#     if not devices:
#         return []

#     result = []
#     for device in devices:
#         # Lấy field của từng thiết bị
#         fields = db.query(DeviceField).filter(DeviceField.thiet_bi_id == device.id).all()
#         result.append({
#             "ma_thiet_bi": device.ma_thiet_bi,
#             "ten_thiet_bi": device.ten_thiet_bi,
#             "fields": [
#                 {"khoa": f.khoa, "don_vi": f.don_vi, "mo_ta": f.mo_ta}
#                 for f in fields
#             ]
#         })

#     return result
@router.get("/rooms/{id}/fields")
def get_room_devices_and_fields(id: int, db: Session = Depends(get_db)):
    # Lấy phòng theo id
    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")

    # Lấy tất cả thiết bị trong phòng
    devices = db.query(Device).filter(Device.phong_id == room.id).all()
    if not devices:
        return []

    result = []
    for device in devices:
        # Lấy field của từng thiết bị
        fields = db.query(DeviceField).filter(DeviceField.thiet_bi_id == device.id).all()
        result.append({
            "ma_thiet_bi": device.ma_thiet_bi,
            "ten_thiet_bi": device.ten_thiet_bi,
            "fields": [
                {"khoa": f.khoa, "don_vi": f.don_vi, "mo_ta": f.mo_ta}
                for f in fields
            ]
        })

    return result

@router.get("/internal/rooms/{ma_phong}/fields", tags=["Internal"])
def get_room_devices_and_fields_internal(ma_phong: str, db: Session = Depends(get_db)):
    # Không có get_current_user
    room = db.query(Room).filter(Room.ma_phong == ma_phong).first()
    if not room:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    devices = db.query(Device).filter(Device.phong_id == room.id).all()
    result = []
    for device in devices:
        fields = db.query(DeviceField).filter(DeviceField.thiet_bi_id == device.id).all()
        result.append({
            "ma_thiet_bi": device.ma_thiet_bi,
            "ten_thiet_bi": device.ten_thiet_bi,
            "fields": [
                {"khoa": f.khoa, "don_vi": f.don_vi, "mo_ta": f.mo_ta}
                for f in fields
            ]
        })
    return result
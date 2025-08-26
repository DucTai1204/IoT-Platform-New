
#devices/routes.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid

from database import get_db
from auth.security import get_current_user
from auth.models import NguoiDung
from rooms.models import Room
from .models import Device, DeviceField, Telemetry
from .schemas import DeviceCreate, DeviceOut, FieldCreate, TelemetryIn, TelemetryOut

router = APIRouter(tags=["Thiết bị"])


# Helper: kiểm tra user sở hữu phòng
def ensure_room_owner(db: Session, room_id: int, user_id: int):
    room = db.query(Room).filter(
        Room.id == room_id,
        Room.nguoi_quan_ly_id == user_id
    ).first()
    if not room:
        raise HTTPException(status_code=403, detail="Bạn không sở hữu phòng này hoặc phòng không tồn tại")


# API: Lấy danh sách thiết bị của user
@router.get("/my-devices", summary="Danh sách thiết bị của user", response_model=List[DeviceOut])
def get_my_devices(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    devices = (
        db.query(Device)
        .join(Room, Room.id == Device.phong_id)
        .filter(Room.nguoi_quan_ly_id == current_user.id)
        .all()
    )
    return devices


# 1) Tạo thiết bị
@router.post("/tao-thiet-bi", summary="Tạo thiết bị, gắn phòng", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(
    body: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    ensure_room_owner(db, body.phong_id, current_user.id)

    # Sinh mã thiết bị unique
    while True:
        generated_code = uuid.uuid4().hex
        if not db.query(Device).filter(Device.ma_thiet_bi == generated_code).first():
            break

    dev = Device(
        ma_thiet_bi=generated_code,
        ten_thiet_bi=body.ten_thiet_bi,
        loai_thiet_bi=body.loai_thiet_bi,
        phong_id=body.phong_id,
        # trang_thai="offline",
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return dev


# 2) Xem chi tiết thiết bị (thêm :int để tránh conflict với /my-devices)
@router.get("/{device_id:int}", summary="Xem chi tiết thiết bị và dữ liệu mới nhất của các field")
def get_device_detail(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    dev = (
        db.query(Device)
        .join(Room, Room.id == Device.phong_id)
        .filter(Device.id == device_id, Room.nguoi_quan_ly_id == current_user.id)
        .first()
    )
    if not dev:
        raise HTTPException(status_code=404, detail="Thiết bị không tồn tại")

    fields = db.query(DeviceField).filter(DeviceField.thiet_bi_id == device_id).all()

    telemetry_data = {}
    for field in fields:
        latest_data = (
            db.query(Telemetry)
            .filter(Telemetry.thiet_bi_id == device_id, Telemetry.khoa == field.khoa)
            .order_by(Telemetry.thoi_gian.desc())
            .first()
        )
        telemetry_data[field.khoa] = {
            "don_vi": field.don_vi,
            "mo_ta": field.mo_ta,
            "latest_value": latest_data.gia_tri if latest_data else None,
            "last_update": latest_data.thoi_gian if latest_data else None
        }

    return {
        "id": dev.id,
        "ma_thiet_bi": dev.ma_thiet_bi,
        "ten_thiet_bi": dev.ten_thiet_bi,
        "loai_thiet_bi": dev.loai_thiet_bi,
        "phong_id": dev.phong_id,
        "trang_thai": dev.trang_thai,
        "fields": telemetry_data
    }


# 3) Đăng ký field cho thiết bị
@router.post("/{device_id:int}/dangki-truong", summary="Nhập các trường cho thiết bị theo id", status_code=status.HTTP_201_CREATED)
def add_fields(
    device_id: int,
    body: List[FieldCreate],
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    dev = (
        db.query(Device)
        .join(Room, Room.id == Device.phong_id)
        .filter(Device.id == device_id, Room.nguoi_quan_ly_id == current_user.id)
        .first()
    )
    if not dev:
        raise HTTPException(status_code=404, detail="Thiết bị không tồn tại")

    errors = []
    for f in body:
        if not f.khoa or not f.don_vi:
            errors.append(f"Thiếu thông tin cho field: {f.khoa or '(không tên)'}")
            continue
        dup = db.query(DeviceField).filter(
            DeviceField.thiet_bi_id == device_id,
            DeviceField.khoa == f.khoa
        ).first()
        if dup:
            errors.append(f"Field '{f.khoa}' đã tồn tại trên thiết bị")

    if errors:
        db.rollback()
        raise HTTPException(status_code=400, detail={"message": "Đăng ký thất bại", "errors": errors})

    new_fields = [
        DeviceField(
            thiet_bi_id=device_id,
            khoa=f.khoa,
            don_vi=f.don_vi,
            mo_ta=f.mo_ta
        )
        for f in body
    ]
    db.add_all(new_fields)
    db.commit()

    return JSONResponse(
        status_code=201,
        content={"message": "Đăng ký thành công", "so_luong": len(new_fields)}
    )


# 4) Gửi dữ liệu telemetry
@router.post("/{device_id:int}/gui-data", summary="Gửi data vào thiết bị dựa vào các trường đã đăng ký", response_model=TelemetryOut, status_code=status.HTTP_201_CREATED)
def publish_telemetry(
    device_id: int,
    body: TelemetryIn,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    dev = (
        db.query(Device)
        .join(Room, Room.id == Device.phong_id)
        .filter(Device.id == device_id, Room.nguoi_quan_ly_id == current_user.id)
        .first()
    )
    if not dev:
        raise HTTPException(status_code=404, detail="Thiết bị không tồn tại")

    exists_field = db.query(DeviceField).filter(
        DeviceField.thiet_bi_id == device_id,
        DeviceField.khoa == body.khoa
    ).first()
    if not exists_field:
        raise HTTPException(status_code=400, detail=f"Field '{body.khoa}' chưa được đăng ký cho thiết bị")

    rec = Telemetry(
        thiet_bi_id=device_id,
        khoa=body.khoa,
        gia_tri=body.gia_tri,
        thoi_gian=body.thoi_gian or None,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

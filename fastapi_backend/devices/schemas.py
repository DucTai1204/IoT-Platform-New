# devices/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

# ----------------------
# 0) Device status update
class TrangThaiEnum(str, Enum):
    online = "online"
    offline = "offline"
    error = "error"

class DeviceStatusUpdate(BaseModel):
    trang_thai: TrangThaiEnum

# ----------------------
# 1) Tạo thiết bị
class DeviceCreate(BaseModel):
    ma_thiet_bi: Optional[str] = None
    ten_thiet_bi: Optional[str] = None
    loai_thiet_bi: Optional[str] = None
    phong_id: int


class DeviceOut(BaseModel):
    id: int
    ma_thiet_bi: str
    ten_thiet_bi: Optional[str]
    loai_thiet_bi: Optional[str]
    phong_id: int
    trang_thai: Optional[str]
    ngay_dang_ky: datetime

    class Config:
        from_attributes = True


# ----------------------
# 2) Đăng ký field cho thiết bị
class FieldCreate(BaseModel):
    khoa: Optional[str]
    don_vi: Optional[str] = None
    mo_ta: Optional[str] = None


class FieldOut(BaseModel):
    id: int
    thiet_bi_id: int
    khoa: str
    don_vi: Optional[str]
    mo_ta: Optional[str]

    class Config:
        from_attributes = True


# ----------------------
# 3) Publish telemetry
class TelemetryIn(BaseModel):
    khoa: str
    gia_tri: str
    thoi_gian: Optional[datetime] = None


class TelemetryOut(BaseModel):
    id: int
    thiet_bi_id: int
    khoa: str
    gia_tri: Optional[float]
    thoi_gian: datetime

    class Config:
        from_attributes = True

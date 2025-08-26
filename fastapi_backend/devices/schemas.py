#devices/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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


# 3) Publish telemetry
class TelemetryIn(BaseModel):
    khoa: str
    gia_tri: str
    thoi_gian: Optional[datetime] = None


class TelemetryOut(BaseModel):
    id: int
    thiet_bi_id: int
    khoa: str
    gia_tri: str
    thoi_gian: datetime

    class Config:
        from_attributes = True

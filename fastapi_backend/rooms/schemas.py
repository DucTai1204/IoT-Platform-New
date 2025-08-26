#rooms/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Schema cho thiết bị
class DeviceOut(BaseModel):
    id: int
    ma_thiet_bi:str
    ten_thiet_bi: str
    loai_thiet_bi: Optional[str]

    class Config:
        from_attributes = True

# Schema cho tạo phòng
class RoomCreate(BaseModel):
    ten_phong: str = Field(..., min_length=1, max_length=100)
    mo_ta: Optional[str] = None
    vi_tri: Optional[str] = None

# Schema cho cập nhật phòng
class RoomUpdate(BaseModel):
    ten_phong: Optional[str] = Field(None, min_length=1, max_length=100)
    mo_ta: Optional[str] = None
    vi_tri: Optional[str] = None

# Schema trả về phòng kèm thiết bị
class RoomOut(BaseModel):
    id: int
    ten_phong: str
    mo_ta: Optional[str]
    vi_tri: Optional[str]
    ngay_tao: datetime
    nguoi_quan_ly_id: Optional[int]
    devices: List[DeviceOut] = []

    class Config:
        from_attributes = True

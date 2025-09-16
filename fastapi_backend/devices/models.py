from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (Column, Integer, String, DateTime, Enum, 
                        ForeignKey, Text, Index, Float, Boolean)
from sqlalchemy.orm import relationship
from database import Base

# ==============================================================================
# ENUMS (Định nghĩa các trạng thái)
# ==============================================================================

class TrangThaiEnum(str, PyEnum):
    """Trạng thái kết nối của thiết bị."""
    online = "online"
    offline = "offline"
    error = "error"

class HealthStatusEnum(str, PyEnum):
    """Trạng thái "sức khỏe" cấu hình của thiết bị."""
    ok = "ok"
    misconfigured = "misconfigured"

# ==============================================================================
# MODELS (Mô hình dữ liệu cho các bảng)
# ==============================================================================

class Device(Base):
    __tablename__ = "thiet_bi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_thiet_bi = Column(String(100), nullable=False, unique=True, index=True)
    ten_thiet_bi = Column(String(100))
    loai_thiet_bi = Column(String(100))
    # firmware_version = Column(String(50), nullable=True) # MỚI: Thêm phiên bản firmware
    phong_id = Column(Integer, ForeignKey("phong.id"))
    
    trang_thai = Column(Enum(TrangThaiEnum, name="trang_thai_enum"), default=TrangThaiEnum.offline, nullable=False)
    health_status = Column(Enum(HealthStatusEnum, name="health_status_enum"), default=HealthStatusEnum.ok, nullable=False) # MỚI: Thêm trạng thái sức khỏe
    
    ngay_dang_ky = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=None, nullable=True)

    # CẬP NHẬT: Hoàn thiện các mối quan hệ
    room = relationship("Room", back_populates="devices")
    fields = relationship("DeviceField", back_populates="device", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="device", cascade="all, delete-orphan")

class DeviceField(Base):
    __tablename__ = "khoa_du_lieu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thiet_bi_id = Column(Integer, ForeignKey("thiet_bi.id"), nullable=False)
    khoa = Column(String(100), nullable=False) # Tên trường dữ liệu, ví dụ: "temp", "hum"
    don_vi = Column(String(50))
    mo_ta = Column(Text)

    # MỚI: Thêm quan hệ ngược lại với Device
    device = relationship("Device", back_populates="fields")

class Telemetry(Base):
    __tablename__ = "du_lieu_thiet_bi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thiet_bi_id = Column(Integer, ForeignKey("thiet_bi.id"), nullable=False)
    khoa = Column(String(100), nullable=False)
    
    # CẬP NHẬT: Đổi kiểu dữ liệu để tối ưu tính toán
    gia_tri = Column(Float, nullable=True)
    
    thoi_gian = Column(DateTime, default=datetime.utcnow, index=True)

    # MỚI: Thêm quan hệ ngược lại với Device
    device = relationship("Device", back_populates="telemetry")

    # TỐI ƯU HÓA: Thêm index để tăng tốc độ truy vấn dữ liệu theo thời gian
    __table_args__ = (
        Index('ix_telemetry_device_id_timestamp', 'thiet_bi_id', 'thoi_gian'),
    )

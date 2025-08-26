#devices/models
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from database import Base
from sqlalchemy.orm import relationship

class Device(Base):
    __tablename__ = "thiet_bi"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_thiet_bi = Column(String(100), nullable=False, unique=True)
    ten_thiet_bi = Column(String(100))
    loai_thiet_bi = Column(String(100))
    phong_id = Column(Integer, ForeignKey("phong.id"))  # phòng (Room)
    trang_thai = Column(Enum("online", "offline", "error", name="trang_thai"), default="offline")
    ngay_dang_ky = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="devices")


class DeviceField(Base):
    __tablename__ = "khoa_du_lieu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thiet_bi_id = Column(Integer, ForeignKey("thiet_bi.id"), nullable=False)
    khoa = Column(String(100), nullable=False)
    don_vi = Column(String(50))
    mo_ta = Column(Text)


class Telemetry(Base):
    __tablename__ = "du_lieu_thiet_bi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thiet_bi_id = Column(Integer, ForeignKey("thiet_bi.id"), nullable=False)
    khoa = Column(String(100), nullable=False)
    gia_tri = Column(Text)
    thoi_gian = Column(DateTime, default=datetime.utcnow)

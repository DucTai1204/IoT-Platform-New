from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

# Enum SQLAlchemy & Pydantic
class TrangThaiEnum(str, PyEnum):
    online = "online"
    offline = "offline"
    error = "error"

class Device(Base):
    __tablename__ = "thiet_bi"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_thiet_bi = Column(String(100), nullable=False, unique=True)
    ten_thiet_bi = Column(String(100))
    loai_thiet_bi = Column(String(100))
    phong_id = Column(Integer, ForeignKey("phong.id"))
    trang_thai = Column(Enum(TrangThaiEnum, name="trang_thai"), default=TrangThaiEnum.offline, nullable=False)
    ngay_dang_ky = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=None, nullable=True)  # thời gian update cuối

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

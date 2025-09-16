from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey, JSON
from database import Base
import enum
from datetime import datetime

class LoaiKenh(str, enum.Enum):
    telegram = "telegram"
    email = "email"
    zalo = "zalo"

class KenhThongBao(Base):
    __tablename__ = "kenh_thong_bao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nguoi_dung_id = Column(Integer, ForeignKey("nguoi_dung.id"), nullable=False)
    loai = Column(Enum(LoaiKenh), nullable=False)
    external_id = Column(String(255), nullable=False)  # telegram chat_id
    cau_hinh = Column(JSON, default=None)
    da_kich_hoat = Column(Boolean, default=True)
    ngay_tao = Column(DateTime, default=datetime.utcnow)
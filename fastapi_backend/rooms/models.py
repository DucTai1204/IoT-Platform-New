# rooms/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Room(Base):
    __tablename__ = "phong"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_phong = Column(String(100))        # tên phòng
    mo_ta = Column(Text)
    vi_tri = Column(String(255))
    nguoi_quan_ly_id = Column(Integer, ForeignKey("nguoi_dung.id"))
    ngay_tao = Column(DateTime, default=datetime.utcnow)

    # Tự sinh mã phòng khi tạo
    ma_phong = Column(String(100), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)

    devices = relationship("Device", back_populates="room")

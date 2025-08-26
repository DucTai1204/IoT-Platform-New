### `auth/models.py`
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from database import Base

# Ánh xạ lại bảng có sẵn: nguoi_dung (id, ten, email, mat_khau_hash, vai_tro, ngay_tao)
class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    mat_khau_hash = Column(Text, nullable=False)
    # giữ Enum khớp với DB hiện có; app không tự tạo bảng
    vai_tro = Column(Enum("admin", "user", name="vai_tro"), default="user")
    ngay_tao = Column(DateTime, default=datetime.utcnow)


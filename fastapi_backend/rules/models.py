# rules/models.py (UPDATED)
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON, Time, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, time, date

Base = declarative_base()

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    ten_rule = Column(String(255))
    phong_id = Column(Integer, nullable=False)
    condition_device_id = Column(String(255), nullable=False)
    field = Column(String(100), nullable=False)
    operator = Column(String(10), nullable=False)
    value = Column(String(100), nullable=False)
    muc_do_uu_tien = Column(Integer, default=1)
    trang_thai = Column(Enum("enabled", "disabled"), default="enabled")
    ngay_tao = Column(DateTime, default=datetime.utcnow)

    actions = relationship("RuleAction", back_populates="rule", cascade="all, delete-orphan")

class RuleAction(Base):
    __tablename__ = "rule_actions"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id", ondelete="CASCADE"))
    device_id = Column(String(255), nullable=False)
    action_command = Column(String(100), nullable=False)
    action_params = Column(JSON, default={})
    delay_seconds = Column(Integer, default=0)
    thu_tu = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    rule = relationship("Rule", back_populates="actions")

class Command(Base):
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False)
    command = Column(String(100), nullable=False)
    payload = Column(JSON, default={})
    status = Column(Enum("pending", "sent", "acked", "failed"), default="pending")
    rule_id = Column(Integer, nullable=True)
    rule_action_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    acked_at = Column(DateTime, nullable=True)
    error_message = Column(String(255), nullable=True)

# ===============================================
# === BẢNG MỚI CHO LỊCH TRÌNH ĐỊNH KỲ (CẬP NHẬT) ===
# ===============================================

class LichTrinhThoiGian(Base):
    __tablename__ = "lich_trinh_thoi_gian"

    id = Column(Integer, primary_key=True, index=True)
    ten_lich = Column(String(255), nullable=False)
    phong_id = Column(Integer, nullable=False)
    thoi_gian_chay = Column(Time, nullable=False)
    
    # Cột mới thay thế cac_ngay_chay
    ngay_bat_dau = Column(Date, nullable=False) # Lịch trình sẽ bắt đầu từ ngày này
    tan_suat = Column(Enum("ONCE", "DAILY", "WEEKLY", "MONTHLY"), default="ONCE") 
    ngay_ket_thuc = Column(Date, nullable=True) # Ngày kết thúc (Nếu cần)
    ngay_lap_lai_tuan = Column(String(50), default=None) # MON,TUE,WED (chỉ dùng nếu tan_suat=WEEKLY)
    
    trang_thai = Column(Enum("active", "disabled"), default="active")
    nguoi_tao_id = Column(Integer)
    ngay_tao = Column(DateTime, default=datetime.utcnow)

    hanh_dongs = relationship("HanhDongDinhKy", back_populates="lich_trinh", cascade="all, delete-orphan")

class HanhDongDinhKy(Base):
    __tablename__ = "hanh_dong_dinh_ky"

    id = Column(Integer, primary_key=True, index=True)
    lich_trinh_id = Column(Integer, ForeignKey("lich_trinh_thoi_gian.id", ondelete="CASCADE"))
    device_id = Column(String(100), nullable=False)
    command = Column(String(100), nullable=False)
    payload = Column(JSON, default={})
    thu_tu = Column(Integer, default=1)

    lich_trinh = relationship("LichTrinhThoiGian", back_populates="hanh_dongs")
#rules/models.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

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

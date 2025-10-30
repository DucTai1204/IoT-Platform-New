# rules/schemas.py (UPDATED)
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, time, date

class RuleActionBase(BaseModel):
    device_id: str
    action_command: str
    action_params: Optional[Dict] = {}
    delay_seconds: Optional[int] = 0
    thu_tu: Optional[int] = 1

class RuleActionCreate(RuleActionBase):
    pass

class RuleAction(RuleActionBase):
    id: int
    rule_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class RuleBase(BaseModel):
    ten_rule: str
    phong_id: int
    condition_device_id: str
    field: str
    operator: str
    value: str
    muc_do_uu_tien: Optional[int] = 1
    trang_thai: Optional[str] = "enabled"

class RuleCreate(RuleBase):
    actions: List[RuleActionCreate]

class Rule(RuleBase):
    id: int
    ngay_tao: datetime
    actions: List[RuleAction] = []

    class Config:
        orm_mode = True

class CommandBase(BaseModel):
    device_id: str
    command: str
    payload: Optional[Dict] = {}
    status: Optional[str] = "pending"

class CommandCreate(CommandBase):
    pass

class Command(CommandBase):
    id: int
    rule_id: Optional[int]
    rule_action_id: Optional[int]
    created_at: datetime
    sent_at: Optional[datetime]
    acked_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        orm_mode = True

# ===============================================
# === SCHEMAS MỚI CHO LỊCH TRÌNH ĐỊNH KỲ (CẬP NHẬT) ===
# ===============================================

class HanhDongDinhKyBase(BaseModel):
    device_id: str
    command: str
    payload: Optional[Dict] = {}
    thu_tu: Optional[int] = 1

class HanhDongDinhKyCreate(HanhDongDinhKyBase):
    pass

class HanhDongDinhKy(HanhDongDinhKyBase):
    id: int
    lich_trinh_id: int

    class Config:
        orm_mode = True

class LichTrinhThoiGianBase(BaseModel):
    ten_lich: str
    phong_id: int
    thoi_gian_chay: time
    
    # Các trường mới thay thế cac_ngay_chay
    ngay_bat_dau: date # Kiểu date
    tan_suat: Optional[str] = "ONCE" # ONCE, DAILY, WEEKLY, MONTHLY
    ngay_ket_thuc: Optional[date] = None
    ngay_lap_lai_tuan: Optional[str] = None # MON,TUE,WED
    
    trang_thai: Optional[str] = "active"

class LichTrinhThoiGianCreate(LichTrinhThoiGianBase):
    hanh_dongs: List[HanhDongDinhKyCreate]

class LichTrinhThoiGian(LichTrinhThoiGianBase):
    id: int
    nguoi_tao_id: Optional[int]
    ngay_tao: datetime
    hanh_dongs: List[HanhDongDinhKy] = []

    class Config:
        orm_mode = True
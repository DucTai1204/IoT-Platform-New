# rules/routes.py (UPDATED)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from . import models, schemas
from datetime import datetime
from devices.models import Device 
router = APIRouter(prefix="/rules", tags=["Rules & Commands"])

# ===============================================
# === API RULES CŨ (GIỮ NGUYÊN) ===
# ===============================================

# Lấy rules theo room_id
@router.get("/", response_model=List[schemas.Rule])
def get_rules(room_id: int, db: Session = Depends(get_db)):
    return db.query(models.Rule)\
             .filter(models.Rule.phong_id == room_id, models.Rule.trang_thai == "enabled")\
             .order_by(models.Rule.muc_do_uu_tien.asc(), models.Rule.ngay_tao.desc())\
             .all()

# Tạo rule mới
@router.post("/", response_model=schemas.Rule)
def create_rule(rule_in: schemas.RuleCreate, db: Session = Depends(get_db)):
    rule = models.Rule(
        ten_rule=rule_in.ten_rule,
        phong_id=rule_in.phong_id,
        condition_device_id=rule_in.condition_device_id,
        field=rule_in.field,
        operator=rule_in.operator,
        value=rule_in.value,
        muc_do_uu_tien=rule_in.muc_do_uu_tien,
        trang_thai=rule_in.trang_thai,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    for action_in in rule_in.actions:
        action = models.RuleAction(
            rule_id=rule.id,
            device_id=action_in.device_id,
            action_command=action_in.action_command,
            action_params=action_in.action_params,
            delay_seconds=action_in.delay_seconds,
            thu_tu=action_in.thu_tu,
        )
        db.add(action)

    db.commit()
    db.refresh(rule)
    return rule


# Xem commands
@router.get("/commands", response_model=List[schemas.Command])
def get_commands(device_id: str, db: Session = Depends(get_db)):
    return db.query(models.Command).filter(models.Command.device_id == device_id).all()

# Xóa rule
@router.delete("/{rule_id}", response_model=dict)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": f"Rule {rule_id} deleted successfully"}

# Sửa rule
@router.put("/{rule_id}", response_model=schemas.Rule)
def update_rule(rule_id: int, rule_in: schemas.RuleCreate, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Cập nhật thông tin chính của rule
    rule.ten_rule = rule_in.ten_rule
    rule.phong_id = rule_in.phong_id
    rule.condition_device_id = rule_in.condition_device_id
    rule.field = rule_in.field
    rule.operator = rule_in.operator
    rule.value = rule_in.value
    rule.muc_do_uu_tien = rule_in.muc_do_uu_tien
    rule.trang_thai = rule_in.trang_thai

    # Xóa actions cũ
    db.query(models.RuleAction).filter(models.RuleAction.rule_id == rule.id).delete()

    # Thêm actions mới
    for action_in in rule_in.actions:
        action = models.RuleAction(
            rule_id=rule.id,
            device_id=action_in.device_id,
            action_command=action_in.action_command,
            action_params=action_in.action_params,
            delay_seconds=action_in.delay_seconds,
            thu_tu=action_in.thu_tu,
        )
        db.add(action)

    db.commit()
    db.refresh(rule)
    return rule
# Lấy tất cả lịch trình theo room_id (ĐÃ SỬ DỤNG CỘT MỚI trong ORDER BY)
@router.get("/schedules", response_model=List[schemas.LichTrinhThoiGian])
def get_schedules(room_id: int, db: Session = Depends(get_db)):
    return db.query(models.LichTrinhThoiGian)\
             .filter(models.LichTrinhThoiGian.phong_id == room_id)\
             .order_by(models.LichTrinhThoiGian.ngay_bat_dau.asc(), models.LichTrinhThoiGian.thoi_gian_chay.asc())\
             .all()

# Tạo lịch trình mới (ĐÃ CẬP NHẬT TRƯỜNG VÀ BẮT LỖI)
@router.post("/schedules", response_model=schemas.LichTrinhThoiGian, status_code=status.HTTP_201_CREATED)
def create_schedule(schedule_in: schemas.LichTrinhThoiGianCreate, db: Session = Depends(get_db)):
    # 1. Thu thập và kiểm tra Device IDs (Logic bắt lỗi 400 rõ ràng)
    action_device_ids = {action.device_id for action in schedule_in.hanh_dongs}
    existing_devices = db.query(Device.ma_thiet_bi).filter(Device.ma_thiet_bi.in_(action_device_ids)).all()
    existing_device_ids = {dev[0] for dev in existing_devices}
    invalid_device_ids = action_device_ids - existing_device_ids

    if invalid_device_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi: Mã thiết bị không tồn tại trong hệ thống. Các mã không hợp lệ: {', '.join(invalid_device_ids)}"
        )
    
    # 2. Tạo và chèn lịch trình 
    schedule = models.LichTrinhThoiGian(
        ten_lich=schedule_in.ten_lich,
        phong_id=schedule_in.phong_id,
        thoi_gian_chay=schedule_in.thoi_gian_chay,
        # Cập nhật các trường mới
        ngay_bat_dau=schedule_in.ngay_bat_dau,
        tan_suat=schedule_in.tan_suat,
        ngay_ket_thuc=schedule_in.ngay_ket_thuc,
        ngay_lap_lai_tuan=schedule_in.ngay_lap_lai_tuan,
        
        trang_thai=schedule_in.trang_thai,
        nguoi_tao_id=5, 
    )
    db.add(schedule)
    db.flush() 
    
    # 3. Thêm HanhDongDinhKy
    for action_in in schedule_in.hanh_dongs:
        action = models.HanhDongDinhKy(
            lich_trinh_id=schedule.id,
            device_id=action_in.device_id,
            command=action_in.command,
            payload=action_in.payload,
            thu_tu=action_in.thu_tu,
        )
        db.add(action)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        # Bắt lỗi 500 nếu có lỗi CSDL khác ngoài Foreign Key
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi CSDL không mong muốn trong quá trình lưu: {e}"
        )

    db.refresh(schedule)
    return schedule

# Cập nhật lịch trình (ĐÃ CẬP NHẬT TRƯỜNG VÀ BẮT LỖI)
@router.put("/schedules/{schedule_id}", response_model=schemas.LichTrinhThoiGian)
def update_schedule(schedule_id: int, schedule_in: schemas.LichTrinhThoiGianCreate, db: Session = Depends(get_db)):
    schedule = db.query(models.LichTrinhThoiGian).filter(models.LichTrinhThoiGian.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # 1. Thu thập và kiểm tra Device IDs (Logic bắt lỗi 400 rõ ràng)
    action_device_ids = {action.device_id for action in schedule_in.hanh_dongs}
    existing_devices = db.query(Device.ma_thiet_bi).filter(Device.ma_thiet_bi.in_(action_device_ids)).all()
    existing_device_ids = {dev[0] for dev in existing_devices}
    invalid_device_ids = action_device_ids - existing_device_ids

    if invalid_device_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi: Mã thiết bị không tồn tại trong hệ thống. Các mã không hợp lệ: {', '.join(invalid_device_ids)}"
        )
        
    # Cập nhật thông tin chính của lịch trình
    schedule.ten_lich = schedule_in.ten_lich
    schedule.phong_id = schedule_in.phong_id
    schedule.thoi_gian_chay = schedule_in.thoi_gian_chay
    # Cập nhật các trường mới
    schedule.ngay_bat_dau=schedule_in.ngay_bat_dau
    schedule.tan_suat=schedule_in.tan_suat
    schedule.ngay_ket_thuc=schedule_in.ngay_ket_thuc
    schedule.ngay_lap_lai_tuan=schedule_in.ngay_lap_lai_tuan
    
    schedule.trang_thai = schedule_in.trang_thai

    # Xóa hành động cũ
    db.query(models.HanhDongDinhKy).filter(models.HanhDongDinhKy.lich_trinh_id == schedule.id).delete()

    # Thêm hành động mới
    for action_in in schedule_in.hanh_dongs:
        action = models.HanhDongDinhKy(
            lich_trinh_id=schedule.id,
            device_id=action_in.device_id,
            command=action_in.command,
            payload=action_in.payload,
            thu_tu=action_in.thu_tu,
        )
        db.add(action)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi CSDL không mong muốn trong quá trình lưu: {e}"
        )
        
    db.refresh(schedule)
    return schedule

# Xóa lịch trình (GIỮ NGUYÊN)
@router.delete("/schedules/{schedule_id}", response_model=dict)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(models.LichTrinhThoiGian).filter(models.LichTrinhThoiGian.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(schedule)
    db.commit()
    return {"message": f"Schedule {schedule_id} deleted successfully"}
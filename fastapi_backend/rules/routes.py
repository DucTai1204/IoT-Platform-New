from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from . import models, schemas

router = APIRouter(prefix="/rules", tags=["Rules & Commands"])

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

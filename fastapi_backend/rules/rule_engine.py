import time
import logging
import threading
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Rule, Command
from .utils import send_command_to_device
from notifications.processor import process_and_send_notification

logger = logging.getLogger(__name__)

class RuleEngine:
    def evaluate_rules(self, db: Session, room_id: int, device_id: str, sensor_data: dict):
        rules = (
            db.query(Rule)
            .filter(Rule.phong_id == room_id, Rule.trang_thai == "enabled")
            .order_by(Rule.muc_do_uu_tien.asc(), Rule.ngay_tao.desc())
            .all()
        )
        for rule in rules:
            if rule.condition_device_id != device_id:
                continue

            val = sensor_data.get(rule.field)
            if val is None:
                continue

            if self._ok(val, rule.operator, rule.value):
                logger.info(f"🎯 Rule '{rule.ten_rule}' (ID: {rule.id}) TRIGGERED!")
                
                # Thực thi các action của rule
                for action in sorted(rule.actions, key=lambda a: a.thu_tu):
                    cmd = Command(
                        device_id=action.device_id,
                        command=action.action_command,
                        payload=action.action_params or {},
                        status="pending",
                        rule_id=rule.id,
                        rule_action_id=action.id,
                        created_at=datetime.utcnow(),
                    )
                    db.add(cmd)
                    db.commit()
                    db.refresh(cmd)

                    if (action.delay_seconds or 0) > 0:
                        time.sleep(action.delay_seconds)

                    send_command_to_device(
                        command_id=cmd.id,
                        device_id=action.device_id,
                        command=action.action_command,
                        payload=action.action_params or {},
                    )
                
                # Bắt đầu tiến trình gửi thông báo trong một luồng (thread) mới
                notification_thread = threading.Thread(
                    target=process_and_send_notification,
                    args=(rule.id, sensor_data)
                )
                notification_thread.start()
                logger.info(f"📨 Notification task for rule '{rule.ten_rule}' started in background.")

    def _ok(self, value, op, threshold) -> bool:
        try:
            value = float(value); threshold = float(threshold)
        except Exception:
            value = str(value); threshold = str(threshold)

        if op == ">":  return value > threshold
        if op == "<":  return value < threshold
        if op == "=":  return value == threshold
        if op == ">=": return value >= threshold
        if op == "<=": return value <= threshold
        if op == "!=": return value != threshold
        return False
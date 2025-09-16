import logging
import html
from typing import List # MỚI
from sqlalchemy.orm import Session, joinedload # MỚI
from database import SessionLocal
from devices.models import Device
from rules.models import Rule
from rooms.models import Room
from .models import KenhThongBao, LoaiKenh
from .telegram import send_telegram_alert

logger = logging.getLogger(__name__)


def _send_alert_to_manager(db: Session, device: Device, message: str):
    """Hàm phụ trợ để tìm người quản lý và gửi tin nhắn."""
    if not device.room or not device.room.nguoi_quan_ly_id:
        return

    manager_id = device.room.nguoi_quan_ly_id
    channels = db.query(KenhThongBao).filter(
        KenhThongBao.nguoi_dung_id == manager_id,
        KenhThongBao.da_kich_hoat == True
    ).all()

    if not channels:
        logger.info(f"Manager (ID: {manager_id}) for device {device.ma_thiet_bi} has no active channels.")
        return

    for channel in channels:
        if channel.loai == LoaiKenh.telegram:
            send_telegram_alert(message, channel.external_id)


def process_and_send_notification(rule_id: int, trigger_data: dict):
    """Xử lý thông báo khi một RULE được kích hoạt."""
    db: Session = SessionLocal()
    try:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule: return

        device = db.query(Device).filter(Device.ma_thiet_bi == rule.condition_device_id).first()
        room = db.query(Room).filter(Room.id == rule.phong_id).first()
        if not device or not room: return

        logger.info(f"Processing RULE notification for rule_id: {rule_id}")
        
        actual_value = trigger_data.get(rule.field, 'N/A')
        condition_text = f"{rule.field} {rule.operator} {rule.value}"
        escaped_condition = html.escape(condition_text)

        message = (
            f"️⚠️ <b>CẢNH BÁO TỰ ĐỘNG</b> ⚠️\n\n"
            f"<b>Phòng:</b> {room.ten_phong}\n"
            f"<b>Rule kích hoạt:</b> {rule.ten_rule}\n"
            f"<b>Điều kiện:</b> <code>{escaped_condition}</code>\n"
            f"<b>Giá trị thực tế:</b> <code>{actual_value}</code>"
        )
        _send_alert_to_manager(db, device, message)

    except Exception as e:
        logger.error(f"Error processing RULE notification for rule {rule_id}: {e}", exc_info=True)
    finally:
        db.close()


def process_device_online_notification(device_id: str):
    """Xử lý thông báo khi một thiết bị ONLINE."""
    db: Session = SessionLocal()
    try:
        device = db.query(Device).options(joinedload(Device.room)).filter(Device.ma_thiet_bi == device_id).first()
        if not device: return

        logger.info(f"Processing ONLINE notification for device_id: {device_id}")
        
        room_name = device.room.ten_phong if device.room else "Không xác định"
        
        message = (
            f"✅ <b>THIẾT BỊ ONLINE</b> ✅\n\n"
            f"<b>Thiết bị:</b> {html.escape(device.ten_thiet_bi or device_id)}\n"
            f"<b>Phòng:</b> {html.escape(room_name)}"
        )
        _send_alert_to_manager(db, device, message)

    except Exception as e:
        logger.error(f"Error processing ONLINE notification for {device_id}: {e}", exc_info=True)
    finally:
        db.close()


def process_device_offline_notification(device_id: str):
    """Xử lý thông báo khi một thiết bị OFFLINE."""
    db: Session = SessionLocal()
    try:
        device = db.query(Device).options(joinedload(Device.room)).filter(Device.ma_thiet_bi == device_id).first()
        if not device: return

        logger.info(f"Processing OFFLINE notification for device_id: {device_id}")
        
        room_name = device.room.ten_phong if device.room else "Không xác định"
        last_seen_str = device.last_seen.strftime('%d-%m-%Y %H:%M:%S') if device.last_seen else "Không rõ"

        message = (
            f"🔴 <b>THIẾT BỊ OFFLINE</b> 🔴\n\n"
            f"<b>Thiết bị:</b> {html.escape(device.ten_thiet_bi or device_id)}\n"
            f"<b>Phòng:</b> {html.escape(room_name)}\n"
            f"<b>Lần cuối thấy:</b> {last_seen_str}"
        )
        _send_alert_to_manager(db, device, message)

    except Exception as e:
        logger.error(f"Error processing OFFLINE notification for {device_id}: {e}", exc_info=True)
    finally:
        db.close()

# MỚI: Thêm hàm xử lý thông báo thiết bị cấu hình sai
def process_device_misconfigured_notification(device_id: str, invalid_fields: List[str]):
    """
    Xử lý và gửi thông báo khi một thiết bị gửi dữ liệu sai cấu hình.
    """
    db: Session = SessionLocal()
    try:
        # Tải sẵn thông tin phòng và người quản lý để tối ưu truy vấn
        device = db.query(Device).options(
            joinedload(Device.room).joinedload(Room.manager)
        ).filter(Device.ma_thiet_bi == device_id).first()
        
        if not device:
            return

        logger.info(f"Processing MISCONFIGURED notification for device_id: {device_id}")

        # Định dạng chuỗi các trường bị sai
        fields_str = ", ".join(f"<code>{html.escape(f)}</code>" for f in invalid_fields)

        message = (
            f"️⚠️ <b>THIẾT BỊ CẤU HÌNH SAI</b> ⚠️\n\n"
            f"<b>Thiết bị:</b> {html.escape(device.ten_thiet_bi or device_id)}\n"
            f"<b>Phòng:</b> {html.escape(device.room.ten_phong if device.room else 'Không xác định')}\n\n"
            f"Thiết bị đang gửi các trường dữ liệu không được khai báo: {fields_str}. "
            f"Vui lòng kiểm tra lại firmware hoặc cấu hình các trường của thiết bị."
        )
        
        _send_alert_to_manager(db, device, message)

    except Exception as e:
        logger.error(f"Error processing MISCONFIGURED notification for {device_id}: {e}", exc_info=True)
    finally:
        db.close()
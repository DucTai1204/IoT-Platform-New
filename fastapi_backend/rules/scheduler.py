# rules/scheduler.py (UPDATED)
import time
import logging
import threading
from datetime import datetime, date, timedelta 
from sqlalchemy.orm import Session
from database import SessionLocal
from .models import LichTrinhThoiGian, HanhDongDinhKy, Command
from .utils import send_command_to_device

logger = logging.getLogger(__name__)

SCHEDULE_CHECK_INTERVAL_SECONDS = 60 

def _should_run_today(schedule: LichTrinhThoiGian, now_date: date) -> bool:
    """Kiểm tra xem lịch trình có nên chạy vào ngày hôm nay không, dựa trên tần suất."""
    
    # 1. Kiểm tra Ngày Kết thúc
    if schedule.ngay_ket_thuc and now_date > schedule.ngay_ket_thuc:
        return False

    # 2. Kiểm tra Ngày Bắt đầu (Lịch trình chỉ nên chạy VÀO hoặc SAU ngày bắt đầu)
    if now_date < schedule.ngay_bat_dau:
        return False

    # 3. Kiểm tra Tần suất
    tan_suat = schedule.tan_suat.upper()
    
    if tan_suat == "ONCE":
        # Chỉ chạy duy nhất một lần vào ngày đã định (ngay_bat_dau)
        return now_date == schedule.ngay_bat_dau
    
    elif tan_suat == "DAILY":
        # Chạy hàng ngày trong khoảng thời gian
        return True
    
    elif tan_suat == "WEEKLY":
        # Chạy hàng tuần vào các ngày lặp lại (MON,TUE...)
        if not schedule.ngay_lap_lai_tuan:
            return False
            
        current_day_of_week = now_date.strftime('%a').upper() # MON, TUE, ...
        scheduled_days = {d.strip().upper() for d in schedule.ngay_lap_lai_tuan.split(',') if d.strip()}
        return current_day_of_week in scheduled_days

    elif tan_suat == "MONTHLY":
        # Chạy vào cùng một ngày trong tháng (vd: ngày 15 hàng tháng)
        return now_date.day == schedule.ngay_bat_dau.day
        
    return False

def execute_schedule_actions(db: Session, lich_trinh_id: int):
    """Thực thi tất cả hành động cho một lịch trình"""
    actions = db.query(HanhDongDinhKy).filter(HanhDongDinhKy.lich_trinh_id == lich_trinh_id).all()

    for action in sorted(actions, key=lambda a: a.thu_tu):
        cmd = Command(
            device_id=action.device_id,
            command=action.command,
            payload=action.payload or {},
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(cmd)
        db.commit()
        db.refresh(cmd)
        
        send_command_to_device(
            command_id=cmd.id,
            device_id=action.device_id,
            command=action.command,
            payload=action.payload or {},
        )
    logger.info(f"✨ SCHEDULE ID {lich_trinh_id} executed commands for {len(actions)} devices.")


def scheduler_loop():
    """Vòng lặp chạy nền để kiểm tra và thực thi lịch trình"""
    while True:
        db = SessionLocal()
        now = datetime.utcnow()
        current_time = now.time().replace(second=0, microsecond=0)
        current_date = now.date() 
        
        try:
            # 1. Tìm kiếm các lịch trình active có thời gian chạy khớp với giờ hiện tại
            schedules = db.query(LichTrinhThoiGian)\
                          .filter(LichTrinhThoiGian.trang_thai == "active",
                                  LichTrinhThoiGian.thoi_gian_chay == current_time)\
                          .all()
            
            for schedule in schedules:
                # 2. Kiểm tra xem lịch trình có nên chạy vào NGÀY HÔM NAY không
                if _should_run_today(schedule, current_date):
                    logger.info(f"🔔 SCHEDULE TRIGGERED: '{schedule.ten_lich}' (ID: {schedule.id})")
                    threading.Thread(
                        target=execute_schedule_actions, 
                        args=(SessionLocal(), schedule.id)
                    ).start()
            
        except Exception as e:
            logger.error(f"❌ Error in scheduler loop: {e}", exc_info=True)
        finally:
            db.close()
        
        time.sleep(SCHEDULE_CHECK_INTERVAL_SECONDS)

def start_scheduler_loop():
    """Khởi động luồng dịch vụ hẹn giờ"""
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    logger.info("⏰ Scheduler service started in background.")
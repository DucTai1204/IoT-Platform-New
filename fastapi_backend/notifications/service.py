from sqlalchemy.orm import Session
from . import models, schemas
from auth.models import NguoiDung
from redis_client import redis_client # <<< 1. Import redis_client

def dang_ky_kenh(db: Session, data: schemas.RegisterChannelByToken, current_user: NguoiDung):
    
    # <<< 2. Sửa logic: Đọc chat_id từ Redis bằng token >>>
    chat_id = redis_client.get(data.token)

    if not chat_id:
        raise Exception("Token không hợp lệ hoặc đã hết hạn. Vui lòng lấy token mới từ bot.")

    # Xóa token khỏi Redis ngay sau khi sử dụng để bảo mật, tránh dùng lại
    redis_client.delete(data.token)

    # Phần logic kiểm tra và lưu vào CSDL MySQL giữ nguyên
    existing = db.query(models.KenhThongBao).filter(
        models.KenhThongBao.nguoi_dung_id == current_user.id,
        models.KenhThongBao.loai == "telegram",
        models.KenhThongBao.external_id == str(chat_id)
    ).first()

    if existing:
        if not existing.da_kich_hoat:
            existing.da_kich_hoat = True
            db.commit()
        return existing

    kenh = models.KenhThongBao(
        nguoi_dung_id=current_user.id,
        loai="telegram",
        external_id=str(chat_id), 
        da_kich_hoat=True
    )
    db.add(kenh)
    db.commit()
    db.refresh(kenh)
    
    return kenh

def get_channels_by_user(db: Session, user_id: int):
    return db.query(models.KenhThongBao).filter(models.KenhThongBao.nguoi_dung_id == user_id).all()
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.security import get_current_user
from auth.models import NguoiDung
from . import schemas, service

router = APIRouter(prefix="/notifications", tags=["Thông báo"])

@router.post(
    "/register-channel",
    summary="Đăng ký kênh thông báo bằng Token từ Bot",
    response_model=schemas.KenhThongBaoOut,
    status_code=status.HTTP_201_CREATED
)
def register_channel(
    body: schemas.RegisterChannelByToken,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    try:
        kenh = service.dang_ky_kenh(db, body, current_user)
        return kenh
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/my-channels",
    summary="Lấy danh sách kênh thông báo của user hiện tại",
    response_model=list[schemas.KenhThongBaoOut]
)
def get_my_channels(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    return service.get_channels_by_user(db, current_user.id)
#auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from .models import NguoiDung
from .schemas import RegisterBody, LoginBody, TokenResponse, UserOut
from .security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.email == body.email).first()
    if not user or not verify_password(body.mat_khau, user.mat_khau_hash):
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        ten=user.ten,
        vai_tro=user.vai_tro,
    )

@router.post("/dang-ky", response_model=TokenResponse)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    user = NguoiDung(ten=body.ten, email=body.email, mat_khau_hash=hash_password(body.mat_khau))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email đã tồn tại")

    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        ten=user.ten,
        vai_tro=user.vai_tro,
    )
# @router.get("/me", response_model=UserOut)
# def me(current_user: NguoiDung = Depends(get_current_user)):
#     return UserOut(
#         id=current_user.id,
#         ten=current_user.ten,
#         email=current_user.email,
#         vai_tro=current_user.vai_tro,
#         ngay_tao=current_user.ngay_tao,
#     )

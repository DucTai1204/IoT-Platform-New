#auth/security
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from sqlalchemy.orm import Session

from database import get_db
from .models import NguoiDung

JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key_12345")
ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)

def hash_password(password: str) -> str:
    """Hash mật khẩu bằng bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Xác thực mật khẩu, trả False nếu hash sai hoặc không nhận diện được"""
    try:
        return pwd_context.verify(plain, hashed)
    except UnknownHashError:
        # Log rõ nguyên nhân
        print(f"❌ Lỗi: Hash '{hashed}' không phải bcrypt hợp lệ.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu không hợp lệ (hash sai định dạng). Vui lòng đăng ký lại tài khoản."
        )

def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Tạo JWT token"""
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_minutes or JWT_EXPIRE_MINUTES)
    
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    to_encode.update({
        "exp": expire,
        "iat": now
    })
    
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return token

async def get_current_user(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> NguoiDung:
    """Lấy user hiện tại từ JWT token"""
    token = creds.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
        
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
            
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token đã hết hạn")
    except JWTClaimsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ")

    user = db.get(NguoiDung, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User không tồn tại")
    
    return user

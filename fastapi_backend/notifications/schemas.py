from pydantic import BaseModel, Field

class RegisterChannelByToken(BaseModel):
    token: str = Field(..., description="Token nhận được từ bot Telegram, vd: TOKEN-123456789")
    loai: str = Field("telegram", description="Loại kênh, hiện tại chỉ hỗ trợ 'telegram'")

class KenhThongBaoOut(BaseModel):
    id: int
    nguoi_dung_id: int
    loai: str
    external_id: str
    da_kich_hoat: bool

    class Config:
        from_attributes = True
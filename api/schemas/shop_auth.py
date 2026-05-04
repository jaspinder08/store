import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class ShopLoginRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class ShopCreateRequest(BaseModel):
    shop_name: str
    owner_name: Optional[str] = None
    shop_type: Optional[str] = None
    gst_number: Optional[str] = None
    shop_image: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None

class ShopVerifyOTPRequest(BaseModel):
    reference_id: uuid.UUID
    otp: str

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

class ShopResponse(BaseModel):
    id: uuid.UUID
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    shop_type: Optional[str] = None
    gst_number: Optional[str] = None
    shop_image: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ShopAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    shop: ShopResponse

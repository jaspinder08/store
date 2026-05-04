import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class SendOTPRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class SendOTPResponse(BaseModel):
    reference_id: uuid.UUID
    cooldown_seconds: int
    expires_in: int

class VerifyOTPRequest(BaseModel):
    reference_id: uuid.UUID
    otp: str

class ResendOTPRequest(BaseModel):
    reference_id: uuid.UUID

class UserResponse(BaseModel):
    id: uuid.UUID
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
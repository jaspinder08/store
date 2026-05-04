import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from datetime import datetime, timedelta
from api.core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from api.models.base import TimestampModel

class OTP(TimestampModel):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shop.id", ondelete="CASCADE"), nullable=True)
    reference_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    otp = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    is_used = Column(Boolean, default=False)
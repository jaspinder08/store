from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from api.models.base import TimestampModel

class Category(TimestampModel):
    __tablename__ = "category"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, unique=True, nullable=False, index=True)
    icon = Column(String, nullable=True)

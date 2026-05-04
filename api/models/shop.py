from sqlalchemy import Column, String
from api.models.base import TimestampModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

class Shop(TimestampModel):
    __tablename__ = "shop"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    shop_name = Column(String, nullable=True)
    owner_name = Column(String, nullable=True)
    shop_type = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)
    shop_image = Column(String, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    role = Column(String, default="shop")
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
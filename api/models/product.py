from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.models.base import TimestampModel

class Product(TimestampModel):
    __tablename__ = "product"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)

    shop = relationship("Shop", backref="products")
    category = relationship("Category", backref="products")

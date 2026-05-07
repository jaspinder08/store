import enum
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.models.base import TimestampModel

class OrderStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    ready_for_delivery = "ready_for_delivery"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    rejected = "rejected"
    cancelled = "cancelled"

class Order(TimestampModel):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shop.id"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    
    user = relationship("User", backref="orders")
    shop = relationship("Shop", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(TimestampModel):
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", backref="order_items")

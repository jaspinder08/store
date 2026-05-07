from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime
from uuid import UUID
from api.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="List of items to order")

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    price: float
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    shop_id: UUID
    total_amount: float
    status: OrderStatus
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

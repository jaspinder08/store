from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0, description="Product price must be greater than 0")
    stock_quantity: int = Field(0, ge=0, description="Stock quantity cannot be negative")
    is_available: bool = Field(True, description="Whether the product is currently available")
    image_url: Optional[str] = Field(None, description="Product image URL")
    category_id: UUID = Field(..., description="ID of the category this product belongs to")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    category_id: Optional[UUID] = None

class ProductResponse(ProductBase):
    id: UUID
    shop_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

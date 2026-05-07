from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the category")
    icon: Optional[str] = Field(None, description="URL or identifier for the category icon")
    is_active: bool = Field(True, description="Whether the category is active")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    icon: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: UUID
    name: str = Field(..., min_length=2, max_length=100, description="Name of the category")
    icon: Optional[str] = Field(None, description="URL or identifier for the category icon")
    is_active: bool = Field(True, description="Whether the category is active")
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

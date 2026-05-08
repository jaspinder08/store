from pydantic import BaseModel
from typing import Any

class ApnaStoreResponse(BaseModel):
    """
    Standard response schema used for wrapping the data.
    """
    success: bool
    data: Any
    status_code: int
    message: str

class ListResponse(BaseModel):
    count: int
    items: list[Any]

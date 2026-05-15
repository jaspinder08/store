from pydantic import BaseModel
from typing import Any, List

class ListData(BaseModel):
    count: int
    items: List[Any]

class ApnaStoreResponse(BaseModel):
    """
    Standard response schema used for wrapping the data.
    """
    success: bool
    data: Any
    status_code: int
    message: str

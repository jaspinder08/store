from fastapi import APIRouter, Depends, status
import logging
from sqlalchemy.orm import Session
from typing import List
from api.endpoints import deps
from api.crud import category as crud_category
from api.schemas.category import CategoryResponse
from api.schemas.base import ApnaStoreResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("", response_model=ApnaStoreResponse, tags=["Categories"])
def get_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all active categories. (Public)
    """
    try:
        categories = crud_category.get_active_categories(db, skip=skip, limit=limit)
        
        return ApnaStoreResponse(
            success=True,
            data=[CategoryResponse.model_validate(c) for c in categories],
            status_code=status.HTTP_200_OK,
            message="Categories retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while retrieving categories."
        )

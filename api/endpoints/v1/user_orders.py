from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from api.endpoints import deps
from api.crud import order as crud_order
from api.crud.auth import get_current_user
from api.schemas.order import OrderCreate, OrderResponse
from api.schemas.base import ApnaStoreResponse
from api.models.user import User
from typing import Optional


router = APIRouter()
logger = logging.getLogger(__name__)
tags: Optional[list] = ["User - Orders"]


@router.post("", response_model=ApnaStoreResponse, tags=tags)
def place_order(
    *,
    db: Session = Depends(deps.get_db),
    body: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Place a new order (User).
    """
    try:
        order, error_msg = crud_order.create_order(db, user_id=current_user.id, order_data=body)
        
        if error_msg:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=error_msg
            )
            
        return ApnaStoreResponse(
            success=True,
            data=OrderResponse.model_validate(order),
            status_code=status.HTTP_201_CREATED,
            message="Order placed successfully."
        )
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while placing the order."
        )

@router.get("", response_model=ApnaStoreResponse, tags=tags)
def get_orders(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's orders.
    """
    try:
        orders = crud_order.get_orders_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
        return ApnaStoreResponse(
            success=True,
            data=[OrderResponse.model_validate(o) for o in orders],
            status_code=status.HTTP_200_OK,
            message="Orders retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

@router.get("/{id}", response_model=ApnaStoreResponse, tags=tags)
def get_order(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get single order details (User).
    """
    try:
        order = crud_order.get_order_by_user(db, user_id=current_user.id, order_id=id)
        if not order:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Order not found."
            )
            
        return ApnaStoreResponse(
            success=True,
            data=OrderResponse.model_validate(order),
            status_code=status.HTTP_200_OK,
            message="Order retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

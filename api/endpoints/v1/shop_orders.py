from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from api.endpoints import deps
from api.crud import order as crud_order
from api.crud.shop_auth import get_current_shop
from api.schemas.order import OrderUpdateStatus, OrderResponse
from api.schemas.base import ApnaStoreResponse
from api.models.shop import Shop

router = APIRouter()
logger = logging.getLogger(__name__)

from typing import Optional
from api.models.order import OrderStatus

@router.get("", response_model=ApnaStoreResponse, tags=["Shop - Orders"])
def get_shop_orders(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Get all orders for the logged-in shop.
    """
    try:
        orders = crud_order.get_orders_by_shop(db, shop_id=current_shop.id, skip=skip, limit=limit, status_filter=status_filter)
        return ApnaStoreResponse(
            success=True,
            data=[OrderResponse.model_validate(o) for o in orders],
            status_code=status.HTTP_200_OK,
            message="Orders retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting shop orders: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

@router.put("/{id}/status", response_model=ApnaStoreResponse, tags=["Shop - Orders"])
def update_order_status(
    id: UUID,
    body: OrderUpdateStatus,
    db: Session = Depends(deps.get_db),
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Update status of an order for the logged-in shop.
    """
    try:
        order = crud_order.get_order_by_shop(db, shop_id=current_shop.id, order_id=id)
        if not order:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Order not found or does not belong to this shop."
            )
            
        from api.models.order import OrderStatus
        
        if order.status in [OrderStatus.rejected, OrderStatus.delivered, OrderStatus.cancelled]:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Order is already {order.status.value} and cannot be modified."
            )
            
        allowed_transitions = {
            OrderStatus.pending: [OrderStatus.accepted, OrderStatus.rejected],
            OrderStatus.accepted: [OrderStatus.ready_for_delivery],
        }
        
        allowed = allowed_transitions.get(order.status, [])
        if body.status not in allowed:
            allowed_names = [a.value for a in allowed]
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Invalid status transition from {order.status.value} to {body.status.value}. Allowed transitions: {allowed_names}"
            )
            
        updated_order = crud_order.update_order_status(db, db_order=order, status_update=body)
        
        return ApnaStoreResponse(
            success=True,
            data=OrderResponse.model_validate(updated_order),
            status_code=status.HTTP_200_OK,
            message="Order status updated successfully."
        )
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from api.endpoints import deps
from api.crud import auth as crud_auth
from api.crud import shop_auth as crud_shop
from api.schemas.shop_auth import ShopCreateRequest, ShopResponse
from api.schemas.base import ApnaStoreResponse, ListData
from api.models.user import User
from uuid import UUID
from api.crud import category as crud_category
from api.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from api.schemas.order import OrderUpdateStatus
from api.models.order import OrderStatus
router = APIRouter()
tags: Optional[list] = ["Admin"]
logger = logging.getLogger(__name__)

@router.post("/shops", response_model=ApnaStoreResponse, tags=["Admin - Shops"])
def admin_create_shop(
    *,
    db: Session = Depends(deps.get_db),
    body: ShopCreateRequest,
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Create a new shop (Admin only).
    """
    try:
        # 🛡️ Role Check
        if current_user.role != "admin":
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_403_FORBIDDEN,
                message="The user does not have enough privileges."
            )

        # 🔍 Check if shop already exists
        existing_shop = crud_shop.get_shop_by_email(db, email=body.email)
        if existing_shop:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Shop with this email already exists."
            )
        
        if body.phone:
            existing_phone = crud_shop.get_shop_by_phone(db, phone=body.phone)
            if existing_phone:
                return ApnaStoreResponse(
                    success=False,
                    data=None,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Shop with this phone already exists."
                )

        # ✨ Create shop
        shop = crud_shop.create_shop(
            db, 
            shop_name=body.shop_name, 
            email=body.email, 
            phone=body.phone,
            owner_name=body.owner_name,
            shop_type=body.shop_type,
            gst_number=body.gst_number,
            shop_image=body.shop_image
        )
        
        return ApnaStoreResponse(
            success=True,
            data=ShopResponse.model_validate(shop),
            status_code=status.HTTP_201_CREATED,
            message="Shop created successfully by admin."
        )
        
    except Exception as e:
        logger.error(f"Error in admin_create_shop: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred during shop creation."
        )

@router.post("/categories", response_model=ApnaStoreResponse, tags=["Admin - Categories"])
def admin_create_category(
    *,
    db: Session = Depends(deps.get_db),
    body: CategoryCreate,
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Create a new category (Admin only).
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="The user does not have enough privileges."
        )

    existing_category = crud_category.get_category_by_name(db, name=body.name)
    if existing_category:
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Category with this name already exists."
        )

    category = crud_category.create_category(db, category=body)
    
    return ApnaStoreResponse(
        success=True,
        data=CategoryResponse.model_validate(category),
        status_code=status.HTTP_201_CREATED,
        message="Category created successfully."
    )

@router.put("/categories/{id}", response_model=ApnaStoreResponse, tags=["Admin - Categories"])
def admin_update_category(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    body: CategoryUpdate,
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Update a category (Admin only).
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="The user does not have enough privileges."
        )

    category = crud_category.get_category(db, category_id=id)
    if not category:
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_404_NOT_FOUND,
            message="Category not found."
        )

    if body.name and body.name != category.name:
        existing_category = crud_category.get_category_by_name(db, name=body.name)
        if existing_category:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Category with this name already exists."
            )

    updated_category = crud_category.update_category(db, db_category=category, category_update=body)
    
    return ApnaStoreResponse(
        success=True,
        data=CategoryResponse.model_validate(updated_category),
        status_code=status.HTTP_200_OK,
        message="Category updated successfully."
    )

@router.delete("/categories/{id}", response_model=ApnaStoreResponse, tags=["Admin - Categories"])
def admin_delete_category(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Soft delete a category (Admin only).
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="The user does not have enough privileges."
        )

    category = crud_category.get_category(db, category_id=id)
    if not category:
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_404_NOT_FOUND,
            message="Category not found."
        )

    crud_category.soft_delete_category(db, db_category=category)
    
    return ApnaStoreResponse(
        success=True,
        data=None,
        status_code=status.HTTP_200_OK,
        message="Category deleted successfully."
    )

@router.get("/categories", response_model=ApnaStoreResponse, tags=["Admin - Categories"])
def admin_get_categories(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Get all categories (Admin only), including inactive ones.
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="The user does not have enough privileges."
        )

    try:
        from api.models.category import Category
        categories = db.query(Category).filter(Category.is_deleted == False).order_by(Category.created_at.desc()).offset(skip).limit(limit).all()
        return ApnaStoreResponse(
            success=True,
            data=ListData(
                count=len(categories),
                items=[CategoryResponse.model_validate(c) for c in categories]
            ),
            status_code=status.HTTP_200_OK,
            message="Categories retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting admin categories: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

@router.get("/orders", response_model=ApnaStoreResponse, tags=["Admin - Orders"])
def admin_get_orders(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Get all orders (Admin only), optionally filtering by status.
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="The user does not have enough privileges."
        )

    try:
        from api.models.order import Order
        query = db.query(Order).filter(Order.is_deleted == False)
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
            
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        from api.schemas.order import OrderResponse
        return ApnaStoreResponse(
            success=True,
            data=ListData(
                count=len(orders),
                items=[OrderResponse.model_validate(o) for o in orders]
            ),
            status_code=status.HTTP_200_OK,
            message="Orders retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting admin orders: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

@router.put("/orders/{id}/status", response_model=ApnaStoreResponse, tags=["Admin - Orders"])
def admin_update_order_status(
    id: UUID,
    body: OrderUpdateStatus,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Update order status (Admin only). Used for marking delivery stages.
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="The user does not have enough privileges."
        )

    try:
        from api.models.order import Order
        order = db.query(Order).filter(Order.id == id, Order.is_deleted == False).first()
        if not order:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Order not found."
            )
            
        if order.status in [OrderStatus.rejected, OrderStatus.delivered, OrderStatus.cancelled]:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Order is already {order.status.value} and cannot be modified."
            )
            
        allowed_transitions = {
            OrderStatus.ready_for_delivery: [OrderStatus.out_for_delivery],
            OrderStatus.out_for_delivery: [OrderStatus.delivered],
        }
        
        allowed = allowed_transitions.get(order.status, [])
        if body.status not in allowed:
            allowed_names = [a.value for a in allowed]
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Invalid status transition for Admin from {order.status.value} to {body.status.value}. Allowed: {allowed_names}"
            )
            
        order.status = body.status
        db.commit()
        db.refresh(order)
        
        from api.schemas.order import OrderResponse
        return ApnaStoreResponse(
            success=True,
            data=OrderResponse.model_validate(order),
            status_code=status.HTTP_200_OK,
            message="Order status updated successfully."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order status by admin: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred."
        )

from api.schemas.shop_auth import ShopUpdateRequest, ShopStatusUpdate
from api.models.shop import Shop

@router.put("/shops/{id}", response_model=ApnaStoreResponse, tags=["Admin - Shops"])
def admin_update_shop(
    id: UUID,
    body: ShopUpdateRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Update shop details (Admin only).
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="Privilege required"
        )
    try:
        shop = db.query(Shop).filter(Shop.id == id).first()
        if not shop:
            return ApnaStoreResponse(
                success=False, 
                data=None, 
                status_code=status.HTTP_404_NOT_FOUND, 
                message="Shop not found."
            )
            
        update_data = body.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(shop, k, v)
        
        db.commit()
        db.refresh(shop)
        
        return ApnaStoreResponse(
            success=True, 
            data=ShopResponse.model_validate(shop), 
            status_code=status.HTTP_200_OK, 
            message="Shop updated successfully."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating shop by admin: {e}")
        return ApnaStoreResponse(
            success=False, 
            data=None, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message="Update failed"
        )

@router.put("/shops/{id}/status", response_model=ApnaStoreResponse, tags=["Admin - Shops"])
def admin_update_shop_status(
    id: UUID,
    body: ShopStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Update shop active status (Admin only).
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_403_FORBIDDEN,
            message="Privilege required"
        )
    try:
        shop = db.query(Shop).filter(Shop.id == id).first()
        if not shop:
            return ApnaStoreResponse(
                success=False, 
                data=None, 
                status_code=status.HTTP_404_NOT_FOUND, 
                message="Shop not found."
            )
            
        shop.is_active = body.is_active
        db.commit()
        db.refresh(shop)
        
        status_msg = "activated" if shop.is_active else "deactivated"
        return ApnaStoreResponse(
            success=True, 
            data=ShopResponse.model_validate(shop), 
            status_code=status.HTTP_200_OK, 
            message=f"Shop {status_msg} successfully."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating shop status by admin: {e}")
        return ApnaStoreResponse(
            success=False, 
            data=None, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message="Status update failed"
        )

from sqlalchemy import or_

@router.get("/shops", response_model=ApnaStoreResponse, tags=["Admin - Shops"])
def admin_get_shops(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Get all shops (Admin only) with optional filtering and search.
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False, 
            data=None, 
            status_code=status.HTTP_403_FORBIDDEN, 
            message="Privilege required."
        )
    
    try:
        from api.models.shop import Shop
        query = db.query(Shop)
        
        if is_active is not None:
            query = query.filter(Shop.is_active == is_active)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Shop.shop_name.ilike(search_term),
                    Shop.owner_name.ilike(search_term),
                    Shop.phone.ilike(search_term),
                    Shop.email.ilike(search_term)
                )
            )
            
        shops = query.order_by(Shop.created_at.desc()).offset(skip).limit(limit).all()
        
        from api.schemas.shop_auth import AdminShopListResponse
        return ApnaStoreResponse(
            success=True,
            data=ListData(
                count=len(shops),
                items=[AdminShopListResponse.model_validate(s) for s in shops]
            ),
            status_code=status.HTTP_200_OK,
            message="Shops retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting admin shops: {e}")
        return ApnaStoreResponse(
            success=False, 
            data=None, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message="An unexpected error occurred."
        )

@router.get("/shops/{id}", response_model=ApnaStoreResponse, tags=["Admin - Shops"])
def admin_get_shop(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(crud_auth.get_current_user)
):
    """
    Get full details of a specific shop by ID (Admin only).
    """
    if current_user.role != "admin":
        return ApnaStoreResponse(
            success=False, 
            data=None, 
            status_code=status.HTTP_403_FORBIDDEN, 
            message="Privilege required."
        )
    
    try:
        from api.models.shop import Shop
        shop = db.query(Shop).filter(Shop.id == id).first()
        if not shop:
            return ApnaStoreResponse(
                success=False, 
                data=None, 
                status_code=status.HTTP_404_NOT_FOUND, 
                message="Shop not found."
            )
            
        from api.schemas.shop_auth import AdminShopDetailResponse
        return ApnaStoreResponse(
            success=True,
            data=AdminShopDetailResponse.model_validate(shop),
            status_code=status.HTTP_200_OK,
            message="Shop retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error getting shop details: {e}")
        return ApnaStoreResponse(
            success=False, 
            data=None, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            message="An unexpected error occurred."
        )

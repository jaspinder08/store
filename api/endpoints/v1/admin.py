import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from api.endpoints import deps
from api.crud import auth as crud_auth
from api.crud import shop_auth as crud_shop
from api.schemas.shop_auth import ShopCreateRequest, ShopResponse
from api.schemas.base import ApnaStoreResponse
from api.models.user import User
from uuid import UUID
from api.crud import category as crud_category
from api.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()
tags: Optional[list] = ["Admin"]
logger = logging.getLogger(__name__)

@router.post("/shops", response_model=ApnaStoreResponse, tags=tags)
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

@router.post("/categories", response_model=ApnaStoreResponse, tags=tags)
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

@router.put("/categories/{id}", response_model=ApnaStoreResponse, tags=tags)
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

@router.delete("/categories/{id}", response_model=ApnaStoreResponse, tags=tags)
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

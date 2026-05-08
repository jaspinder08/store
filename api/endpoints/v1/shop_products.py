from fastapi import APIRouter, Depends, status, Query
import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from api.endpoints import deps
from api.crud import product as crud_product
from api.crud import category as crud_category
from api.crud.shop_auth import get_current_shop
from api.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from api.schemas.base import ApnaStoreResponse
from api.models.shop import Shop

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=ApnaStoreResponse, tags=["Shop - Products"])
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    body: ProductCreate,
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Create a new product for the logged-in shop.
    """
    try:
        # Validate category exists and is active
        category = crud_category.get_category(db, category_id=body.category_id)
        if not category or not category.is_active:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Category does not exist or is inactive."
            )
            
        product = crud_product.create_product(db, product=body, shop_id=current_shop.id)
        
        return ApnaStoreResponse(
            success=True,
            data=ProductResponse.model_validate(product),
            status_code=status.HTTP_201_CREATED,
            message="Product created successfully."
        )
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while creating product."
        )

@router.get("", response_model=ApnaStoreResponse, tags=["Shop - Products"])
def get_products(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Get all products for the logged-in shop with optional search and filter.
    """
    try:
        products = crud_product.get_products_by_shop(
            db, 
            shop_id=current_shop.id, 
            skip=skip, 
            limit=limit,
            search=search,
            category_id=category_id
        )
        
        return ApnaStoreResponse(
            success=True,
            data=[ProductResponse.model_validate(p) for p in products],
            status_code=status.HTTP_200_OK,
            message="Products retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while retrieving products."
        )

@router.get("/{id}", response_model=ApnaStoreResponse, tags=["Shop - Products"])
def get_product(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Get a single product (only if it belongs to the logged-in shop).
    """
    try:
        product = crud_product.get_product(db, product_id=id, shop_id=current_shop.id)
        if not product:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Product not found or does not belong to this shop."
            )
            
        return ApnaStoreResponse(
            success=True,
            data=ProductResponse.model_validate(product),
            status_code=status.HTTP_200_OK,
            message="Product retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error retrieving product: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while retrieving product."
        )

@router.put("/{id}", response_model=ApnaStoreResponse, tags=["Shop - Products"])
def update_product(
    id: UUID,
    body: ProductUpdate,
    db: Session = Depends(deps.get_db),
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Update a product (only if it belongs to the logged-in shop).
    """
    try:
        product = crud_product.get_product(db, product_id=id, shop_id=current_shop.id)
        if not product:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Product not found or does not belong to this shop."
            )
            
        # Validate category if it's being updated
        if body.category_id:
            category = crud_category.get_category(db, category_id=body.category_id)
            if not category or not category.is_active:
                return ApnaStoreResponse(
                    success=False,
                    data=None,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Category does not exist or is inactive."
                )
                
        updated_product = crud_product.update_product(db, db_product=product, product_update=body)
        
        return ApnaStoreResponse(
            success=True,
            data=ProductResponse.model_validate(updated_product),
            status_code=status.HTTP_200_OK,
            message="Product updated successfully."
        )
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while updating product."
        )

@router.delete("/{id}", response_model=ApnaStoreResponse, tags=["Shop - Products"])
def delete_product(
    id: UUID,
    db: Session = Depends(deps.get_db),
    current_shop: Shop = Depends(get_current_shop)
):
    """
    Soft delete a product (only if it belongs to the logged-in shop).
    """
    try:
        product = crud_product.get_product(db, product_id=id, shop_id=current_shop.id)
        if not product:
            return ApnaStoreResponse(
                success=False,
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Product not found or does not belong to this shop."
            )
            
        crud_product.soft_delete_product(db, db_product=product)
        
        return ApnaStoreResponse(
            success=True,
            data=None,
            status_code=status.HTTP_200_OK,
            message="Product deleted successfully."
        )
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return ApnaStoreResponse(
            success=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred while deleting product."
        )

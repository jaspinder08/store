from sqlalchemy.orm import Session
from sqlalchemy import or_
from api.models.product import Product
from api.schemas.product import ProductCreate, ProductUpdate
from uuid import UUID
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_product(db: Session, product_id: UUID, shop_id: UUID):
    try:
        return db.query(Product).filter(
            Product.id == product_id,
            Product.shop_id == shop_id,
            Product.is_deleted == False
        ).first()
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise e

def get_products_by_shop(
    db: Session, 
    shop_id: UUID, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[UUID] = None
):
    try:
        query = db.query(Product).filter(
            Product.shop_id == shop_id,
            Product.is_deleted == False
        )
        
        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
            
        return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching products for shop {shop_id}: {e}")
        raise e

def create_product(db: Session, product: ProductCreate, shop_id: UUID):
    try:
        db_product = Product(
            **product.model_dump(),
            shop_id=shop_id
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}")
        raise e

def update_product(db: Session, db_product: Product, product_update: ProductUpdate):
    try:
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product {db_product.id}: {e}")
        raise e

def soft_delete_product(db: Session, db_product: Product):
    try:
        db_product.is_available = False
        db_product.is_deleted = True
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error soft deleting product {db_product.id}: {e}")
        raise e

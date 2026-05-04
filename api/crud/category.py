from sqlalchemy.orm import Session
from api.models.category import Category
from api.schemas.category import CategoryCreate, CategoryUpdate
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

def get_category_by_name(db: Session, name: str):
    try:
        return db.query(Category).filter(Category.name == name, Category.is_deleted == False).first()
    except Exception as e:
        logger.error(f"Error fetching category by name {name}: {e}")
        raise e

def get_category(db: Session, category_id: UUID):
    try:
        return db.query(Category).filter(Category.id == category_id, Category.is_deleted == False).first()
    except Exception as e:
        logger.error(f"Error fetching category by ID {category_id}: {e}")
        raise e

def get_active_categories(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Category).filter(Category.is_active == True, Category.is_deleted == False).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching active categories: {e}")
        raise e

def create_category(db: Session, category: CategoryCreate):
    try:
        db_category = Category(
            name=category.name,
            icon=category.icon,
            is_active=category.is_active
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category: {e}")
        raise e

def update_category(db: Session, db_category: Category, category_update: CategoryUpdate):
    try:
        update_data = category_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating category {db_category.id}: {e}")
        raise e

def soft_delete_category(db: Session, db_category: Category):
    try:
        db_category.is_active = False
        db_category.is_deleted = True
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        logger.error(f"Error soft deleting category {db_category.id}: {e}")
        raise e

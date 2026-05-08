from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple, Optional
from api.models.order import Order, OrderItem, OrderStatus
from api.models.product import Product
from api.schemas.order import OrderCreate, OrderUpdateStatus
import logging

logger = logging.getLogger(__name__)

def create_order(db: Session, user_id: UUID, order_data: OrderCreate) -> Tuple[Optional[Order], Optional[str]]:
    try:
        product_ids = [item.product_id for item in order_data.items]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        product_map = {p.id: p for p in products}
        
        total_amount = 0.0
        order_items = []
        shop_id = None
        
        for item in order_data.items:
            product = product_map.get(item.product_id)
            if not product:
                return None, f"Product {item.product_id} not found."
                
            if shop_id is None:
                shop_id = product.shop_id
            elif product.shop_id != shop_id:
                return None, "All items in the order must belong to the same shop."
                
            if not product.is_available or product.is_deleted:
                return None, f"Product {product.name} is currently unavailable."
                
            if product.stock_quantity < item.quantity:
                return None, f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
            
            # Deduct stock immediately
            product.stock_quantity -= item.quantity
            
            price = product.price
            total_amount += price * item.quantity
            
            order_items.append(OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price=price
            ))
            
        db_order = Order(
            user_id=user_id,
            shop_id=shop_id,
            total_amount=total_amount,
            status=OrderStatus.pending
        )
        db.add(db_order)
        db.flush() 
        
        for o_item in order_items:
            o_item.order_id = db_order.id
            db.add(o_item)
            
        db.commit()
        db.refresh(db_order)
        return db_order, None
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating order: {e}")
        raise e

def get_orders_by_user(db: Session, user_id: UUID, skip: int = 0, limit: int = 100):
    try:
        return db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_deleted == False
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting user orders: {e}")
        raise e

def get_order_by_user(db: Session, user_id: UUID, order_id: UUID):
    try:
        return db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.is_deleted == False
        ).first()
    except Exception as e:
        logger.error(f"Error getting user order: {e}")
        raise e

def get_orders_by_shop(db: Session, shop_id: UUID, skip: int = 0, limit: int = 100, status_filter: Optional[OrderStatus] = None):
    try:
        query = db.query(Order).filter(
            Order.shop_id == shop_id,
            Order.is_deleted == False
        )
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
            
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error getting shop orders: {e}")
        raise e

def get_order_by_shop(db: Session, shop_id: UUID, order_id: UUID):
    try:
        return db.query(Order).filter(
            Order.id == order_id,
            Order.shop_id == shop_id,
            Order.is_deleted == False
        ).first()
    except Exception as e:
        logger.error(f"Error getting shop order: {e}")
        raise e

def update_order_status(db: Session, db_order: Order, status_update: OrderUpdateStatus):
    try:
        db_order.status = status_update.status
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating order status: {e}")
        raise e

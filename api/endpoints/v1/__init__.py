from fastapi import APIRouter
from . import auth
from . import shop_auth
from . import admin
from . import categories
from . import shop_products
from . import orders
from . import shop_orders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(orders.router, prefix="/orders")
api_router.include_router(shop_auth.router, prefix="/shop")
api_router.include_router(shop_products.router, prefix="/shop/products")
api_router.include_router(shop_orders.router, prefix="/shop/orders")
api_router.include_router(admin.router, prefix="/admin")
api_router.include_router(categories.router, prefix="/categories")

from fastapi import APIRouter
from . import user_auth
from . import shop_auth
from . import admin
from . import categories
from . import shop_products
from . import user_orders
from . import shop_orders

from . import admin_auth

api_router = APIRouter()

api_router.include_router(user_auth.router, prefix="/auth")
api_router.include_router(user_orders.router, prefix="/orders")
api_router.include_router(shop_auth.router, prefix="/shop")
api_router.include_router(shop_products.router, prefix="/shop/products")
api_router.include_router(shop_orders.router, prefix="/shop/orders")
api_router.include_router(admin_auth.router, prefix="/admin")
api_router.include_router(admin.router, prefix="/admin")
api_router.include_router(categories.router, prefix="/categories")

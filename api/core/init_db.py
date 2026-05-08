from sqlalchemy.orm import Session
from api.core.database import engine, Base, SessionLocal
from api.models.user import User
from api.models import *  # Ensure all models are loaded for create_all

def init_db() -> None:
    """
    Initialize the database: create tables and seed initial data.
    """
    # 🏗️ Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # 🌱 Seed initial data
    db = SessionLocal()
    try:
        from api.core import security
        admin_email = "admin@gmail.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"🚀 Auto-seeding Admin: {admin_email}")
            new_admin = User(
                email=admin_email,
                username="admin",
                role="admin",
                password=security.get_password_hash("password"),
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            
        # Seed categories
        from api.models.category import Category
        initial_categories = [
            "Grocery",
            "Fruits & Vegetables",
            "Dairy",
            "Snacks",
            "Beverages",
            "Bakery",
            "Personal Care",
            "Household Essentials",
            "Cleaning Supplies",
            "Stationery & Miscellaneous"
        ]
        for cat_name in initial_categories:
            cat = db.query(Category).filter(Category.name == cat_name).first()
            if not cat:
                print(f"🛒 Auto-seeding Category: {cat_name}")
                new_cat = Category(name=cat_name, is_active=True)
                db.add(new_cat)
        db.commit()
    except Exception as e:
        print(f"⚠️ Seeding error: {e}")
        db.rollback()
    finally:
        db.close()

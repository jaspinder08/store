import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.core.database import SessionLocal
from api.models.user import User

def seed_admin():
    db = SessionLocal()
    try:
        admin_email = "jaspinder.office@gmail.com"
        
        # 🔍 Check if admin already exists
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if admin:
            print(f"✅ Admin with email {admin_email} already exists.")
            if admin.role != "admin":
                print(f"⚠️ User exists but role is '{admin.role}'. Updating to 'admin'...")
                admin.role = "admin"
                db.commit()
                print("✨ Role updated successfully.")
        else:
            print(f"🚀 Creating new admin user: {admin_email}")
            new_admin = User(
                email=admin_email,
                username="admin",
                role="admin",
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("🎉 Admin user created successfully!")
            
    except Exception as e:
        print(f"❌ Error seeding admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()

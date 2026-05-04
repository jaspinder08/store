import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.core.database import engine, Base
from api.models import *  # This is important to load all models

def reset_database():
    print("⚠️  Warning: This will delete all data in your database.")
    confirm = input("Are you sure you want to recreate the database tables? (y/n): ")
    
    if confirm.lower() == 'y':
        print("🛑 Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("🏗️  Creating all tables with new schema (UUIDs and new columns)...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database reset complete!")
        print("💡 Hint: Run `python scripts/seed_admin.py` to restore your admin user.")
    else:
        print("❌ Operation cancelled.")

if __name__ == "__main__":
    reset_database()

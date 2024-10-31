# scripts/init_db.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, init_db
from app.models.stock import Base

def main():
    try:
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        print("Creating new tables...")
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
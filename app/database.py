from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

# Database configuration
if settings.database_url:
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine("sqlite:///./bookthrift.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add this function to create tables
def create_tables():
    """Create all database tables"""
    from sqlalchemy import text
    from app.models.user import User  # Import your models here
    from app.models.book import Book
    from app.models.wishlist import Wishlist
    from app.models.cart import Cart
    
    # Attempt to add the new column to existing database
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE books ADD COLUMN is_sold BOOLEAN DEFAULT 0"))
    except Exception:
        pass # Column likely already exists
        
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE wishlist ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
    except Exception:
        pass # Column likely already exists
        
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
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
    from app.models.user import User  # Import your models here
    from app.models.book import Book
    from app.models.wishlist import Wishlist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

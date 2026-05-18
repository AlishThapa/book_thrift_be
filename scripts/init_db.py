"""Create database tables for the project."""
from app.database import Base, engine
# Import all models so they are registered on Base.metadata
import app.models.user

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if not existing)")

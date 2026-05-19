from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True, nullable=False)
    condition = Column(String, nullable=False)  # new, like new, used, old
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    images = Column(JSON, nullable=True)  # List of image URLs/paths (max 5)
    is_sold = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", backref="books")

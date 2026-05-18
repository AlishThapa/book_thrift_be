from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base

class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'book_id', name='_user_book_uc'),)

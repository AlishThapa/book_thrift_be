from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import Book
from app.schemas.book import BookResponse as BookSchema
from app.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/my-listings", tags=["Books"])
def get_my_listings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    active_books = db.query(Book).filter(Book.owner_id == current_user.id, Book.is_sold == False).all()
    sold_books = db.query(Book).filter(Book.owner_id == current_user.id, Book.is_sold == True).all()

    return {
        "data": {
            "active": [BookSchema.from_orm(book) for book in active_books],
            "sold": [BookSchema.from_orm(book) for book in sold_books]
        },
        "message": "Successfully retrieved your listings."
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.book import Book
from app.schemas.book import BookListResponse, BookSingleResponse
from app.auth import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/api", tags=["bin"])

@router.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this book")

    book.is_deleted = True
    book.deleted_at = datetime.utcnow()
    db.commit()

    return {"message": "Book moved to bin"}

@router.get("/bin", response_model=BookListResponse)
def get_bin(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    books = db.query(Book).filter(Book.owner_id == current_user.id, Book.is_deleted == True).all()
    return {
        "data": books,
        "message": "Bin fetched successfully"
    }

@router.post("/books/{book_id}/recover", status_code=status.HTTP_200_OK)
def recover_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id, Book.owner_id == current_user.id).first()

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found in bin")

    book.is_deleted = False
    book.deleted_at = None
    db.commit()

    return {"message": "Book recovered successfully"}

@router.delete("/bin/{book_id}", status_code=status.HTTP_200_OK)
def permanently_delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id, Book.owner_id == current_user.id, Book.is_deleted == True).first()

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found in bin")

    db.delete(book)
    db.commit()

    return {"message": "Book permanently deleted"}

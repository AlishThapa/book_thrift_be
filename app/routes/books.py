from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import os
import uuid
from datetime import datetime
from app.database import get_db
from app.models.book import Book
from app.schemas.book import BookListResponse, BookSingleResponse, BookUpdate, DeleteResponse
from app.schemas.wishlist import WishlistToggleResponse
from app.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.models.wishlist import Wishlist

router = APIRouter(prefix="/api", tags=["books"])

UPLOAD_DIR = "uploads"

@router.post("/post-book", response_model=BookSingleResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    title: str = Form(...),
    condition: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(1),
    description: str = Form(""),
    location: str = Form(...),
    category: str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate condition
    condition = condition.lower()
    if condition not in ["new", "like new", "used", "old"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Condition must be one of: new, like new, used, old"
        )

    # Validate quantity
    if quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1"
        )

    # Validate price
    if price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative"
        )

    # Handle image uploads
    image_urls = []
    if images and images[0].filename != "": # Check if files were actually uploaded
        if len(images) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 images allowed"
            )

        for image in images:
            file_extension = os.path.splitext(image.filename)[1]
            if not file_extension:
                file_extension = ".jpg" # Default extension if missing

            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            try:
                with open(file_path, "wb") as buffer:
                    content = await image.read()
                    buffer.write(content)
                image_urls.append(f"/uploads/{unique_filename}")
            except Exception as e:
                print(f"File upload error: {e}")
                # Continue with other images or handle error

    db_book = Book(
        title=title,
        condition=condition,
        price=price,
        quantity=quantity,
        description=description,
        location=location,
        category=category,
        images=image_urls,
        owner_id=current_user.id
    )

    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    return {
        "data": db_book,
        "message": "Book posted successfully"
    }

@router.put("/edit-book/{book_id}", response_model=BookSingleResponse)
async def edit_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the book
    db_book = db.query(Book).filter(Book.id == book_id, Book.is_deleted == False).first()

    # Check if the book exists
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    # Check if the current user is the owner
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to edit this book")

    # Check if the book is sold
    if db_book.is_sold:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot edit a sold book")

    # Update the book with new data
    update_data = book_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)

    return {
        "data": db_book,
        "message": "Book updated successfully"
    }

@router.delete("/delete-book/{book_id}", response_model=DeleteResponse)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the book
    db_book = db.query(Book).filter(Book.id == book_id, Book.is_deleted == False).first()

    # Check if the book exists
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    # Check if the current user is the owner
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this book")

    # Check if the book is sold
    if db_book.is_sold:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a sold book")

    # Perform a soft delete
    db_book.is_deleted = True
    db_book.deleted_at = datetime.utcnow()
    db.commit()

    return {
        "data": None,
        "message": "Book deleted successfully"
    }

@router.put("/update-book-status/{book_id}", response_model=BookSingleResponse)
def update_book_status(
    book_id: int,
    is_sold: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the book
    db_book = db.query(Book).filter(Book.id == book_id, Book.is_deleted == False).first()

    # Check if the book exists
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    # Check if the current user is the owner
    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this book")

    # Update the is_sold status
    db_book.is_sold = is_sold
    db.commit()
    db.refresh(db_book)

    return {
        "data": db_book,
        "message": f"Book status updated to {'sold' if is_sold else 'active'}"
    }

@router.get("/get-books", response_model=BookListResponse)
def get_books(
    category: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Book).options(joinedload(Book.owner)).filter(Book.is_deleted == False)

    if category:
        # If multiple categories are provided, filter by any of them
        query = query.filter(Book.category.in_(category))
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Book.title.ilike(search_filter)) | 
            (Book.description.ilike(search_filter))
        )
    
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    books = query.all()

    if current_user:
        user_wishlist = db.query(Wishlist.book_id).filter(Wishlist.user_id == current_user.id).all()
        wishlisted_book_ids = {book_id for (book_id,) in user_wishlist}

        for book in books:
            book.is_wishlisted = book.id in wishlisted_book_ids
    else:
        for book in books:
            book.is_wishlisted = False

    return {
        "data": books,
        "message": "Books fetched successfully"
    }

@router.get("/book-details", response_model=BookSingleResponse)
def get_book_details(
    book_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    book = db.query(Book).options(joinedload(Book.owner)).filter(Book.id == book_id, Book.is_deleted == False).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    if current_user:
        wishlist_item = db.query(Wishlist).filter(Wishlist.user_id == current_user.id, Wishlist.book_id == book_id).first()
        book.is_wishlisted = wishlist_item is not None
    else:
        book.is_wishlisted = False

    return {
        "data": book,
        "message": "Book details fetched successfully"
    }

@router.post("/toggle-wishlist", response_model=WishlistToggleResponse)
def toggle_wishlist(
    book_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the book exists and is not deleted
    book = db.query(Book).filter(Book.id == book_id, Book.is_deleted == False).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Check if it's already in the wishlist
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.book_id == book_id
    ).first()

    if wishlist_item:
        # Remove from wishlist
        db.delete(wishlist_item)
        db.commit()
        is_wishlisted = False
        message = "Book removed from wishlist"
    else:
        # Add to wishlist
        new_wishlist_item = Wishlist(user_id=current_user.id, book_id=book_id)
        db.add(new_wishlist_item)
        db.commit()
        is_wishlisted = True
        message = "Book added to wishlist"

    return {
        "data": {"book_id": book_id, "is_wishlisted": is_wishlisted},
        "message": message
    }

@router.get("/wishlist", response_model=BookListResponse)
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all wishlisted books for the user
    wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()
    wishlisted_book_ids = [item.book_id for item in wishlist_items]

    if not wishlisted_book_ids:
        return {
            "data": [],
            "message": "Wishlist is empty"
        }

    books = db.query(Book).options(joinedload(Book.owner)).filter(Book.id.in_(wishlisted_book_ids), Book.is_deleted == False).all()

    # All these books are wishlisted
    for book in books:
        book.is_wishlisted = True

    return {
        "data": books,
        "message": "Wishlist fetched successfully"
    }

@router.get("/my-listings", response_model=BookListResponse)
def get_my_listings(
    listing_status: str = Query("active", description="Filter by status: 'active', 'sold', or 'all'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Book).filter(Book.owner_id == current_user.id, Book.is_deleted == False)

    if listing_status == "active":
        query = query.filter(Book.is_sold == False)
    elif listing_status == "sold":
        query = query.filter(Book.is_sold == True)
    elif listing_status != "all":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status parameter. Use 'active', 'sold', or 'all'."
        )

    books = query.all()

    return {
        "data": books,
        "message": f"Successfully retrieved {listing_status} listings."
    }
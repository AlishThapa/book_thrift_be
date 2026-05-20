from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
import os
import uuid
from datetime import datetime
import random
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
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
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
        latitude=latitude,
        longitude=longitude,
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

@router.get("/get-books", response_model=BookListResponse)
def get_books(
    request: Request,
    search: Optional[str] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Book).filter(Book.is_deleted == False, Book.is_sold == False)

    if search:
        query = query.filter(Book.title.ilike(f"%{search}%"))
    
    if condition:
        query = query.filter(Book.condition == condition)

    if category:
        query = query.filter(Book.category == category)

    if min_price is not None:
        query = query.filter(Book.price >= min_price)

    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    if sort_by:
        if sort_by == "price_asc":
            query = query.order_by(Book.price.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Book.price.desc())
        elif sort_by == "date_desc":
            query = query.order_by(Book.created_at.desc())
        elif sort_by == "date_asc":
            query = query.order_by(Book.created_at.asc())
        elif sort_by == "popularity":
            query = query.outerjoin(Wishlist, Book.id == Wishlist.book_id)\
                         .group_by(Book.id)\
                         .order_by(func.count(Wishlist.book_id).desc())

    # Pagination
    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()

    if current_user:
        wishlist_book_ids = {item.book_id for item in db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()}
        for book in books:
            book.is_wishlisted = book.id in wishlist_book_ids

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if current_user:
        book.is_wishlisted = db.query(Wishlist).filter(
            Wishlist.user_id == current_user.id,
            Wishlist.book_id == book_id
        ).first() is not None

    # Get 4 similar books from the same category, excluding the current book
    similar_books = db.query(Book).filter(
        Book.category == book.category,
        Book.id != book.id,
        Book.is_deleted == False,
        Book.is_sold == False
    ).order_by(func.random()).limit(4).all()

    # If there are similar books, attach them to the book response
    if similar_books:
        if current_user:
            wishlist_book_ids = {item.book_id for item in db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()}
            for b in similar_books:
                b.is_wishlisted = b.id in wishlist_book_ids
        book.similar_books = similar_books

    return {
        "data": book,
        "message": "Book details fetched successfully"
    }

@router.put("/update-book/{book_id}", response_model=BookSingleResponse)
async def update_book(
    book_id: int,
    title: str = Form(None),
    condition: str = Form(None),
    price: float = Form(None),
    quantity: int = Form(None),
    description: str = Form(None),
    location: str = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    category: str = Form(None),
    images: List[UploadFile] = File(None),
    is_sold: bool = Form(None),
    is_deleted: bool = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this book")

    update_data = {
        "title": title,
        "condition": condition,
        "price": price,
        "quantity": quantity,
        "description": description,
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "category": category,
        "is_sold": is_sold,
        "is_deleted": is_deleted
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}

    if condition:
        condition = condition.lower()
        if condition not in ["new", "like new", "used", "old"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Condition must be one of: new, like new, used, old"
            )
        update_data["condition"] = condition

    if quantity is not None and quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be at least 1"
        )

    if price is not None and price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative"
        )

    if is_deleted:
        db_book.is_deleted = True
        db_book.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(db_book)
        return {
            "data": db_book,
            "message": "Book marked as deleted"
        }

    # Handle image uploads
    if images and images[0].filename != "":
        if len(images) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 images allowed"
            )

        image_urls = []
        for image in images:
            file_extension = os.path.splitext(image.filename)[1]
            if not file_extension:
                file_extension = ".jpg"

            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            try:
                with open(file_path, "wb") as buffer:
                    content = await image.read()
                    buffer.write(content)
                image_urls.append(f"/uploads/{unique_filename}")
            except Exception as e:
                print(f"File upload error: {e}")
        
        update_data["images"] = image_urls

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
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if db_book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this book")

    db.delete(db_book)
    db.commit()

    return {
        "data": None,
        "message": "Book deleted permanently"
    }

@router.post("/wishlist/toggle/{book_id}", response_model=WishlistToggleResponse)
def toggle_wishlist(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    wishlist_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.book_id == book_id
    ).first()

    if wishlist_item:
        db.delete(wishlist_item)
        db.commit()
        return {
            "data": {"book_id": book_id, "is_wishlisted": False},
            "message": "Book removed from wishlist"
        }
    else:
        new_wishlist_item = Wishlist(user_id=current_user.id, book_id=book_id)
        db.add(new_wishlist_item)
        db.commit()
        return {
            "data": {"book_id": book_id, "is_wishlisted": True},
            "message": "Book added to wishlist"
        }

@router.get("/wishlist", response_model=BookListResponse)
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wishlisted_books = db.query(Book).join(Wishlist).filter(Wishlist.user_id == current_user.id).all()
    
    for book in wishlisted_books:
        book.is_wishlisted = True

    return {
        "data": wishlisted_books,
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

    my_books = query.all()
    
    wishlist_book_ids = {item.book_id for item in db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()}
    for book in my_books:
        book.is_wishlisted = book.id in wishlist_book_ids

    return {
        "data": my_books,
        "message": f"Successfully retrieved {listing_status} listings."
    }

@router.get("/get-random-books", response_model=BookListResponse)
def get_random_books(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    random_books = db.query(Book).filter(Book.is_deleted == False, Book.is_sold == False).order_by(func.random()).limit(10).all()

    if current_user:
        wishlist_book_ids = {item.book_id for item in db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()}
        for book in random_books:
            book.is_wishlisted = book.id in wishlist_book_ids
            
    return {
        "data": random_books,
        "message": "Random books fetched successfully"
    }
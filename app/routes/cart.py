from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, Book, User
from app.schemas import cart as cart_schema
from app.auth import get_current_user

router = APIRouter(
    prefix="/api/cart",
    tags=["cart"],
)


@router.post("/add", response_model=cart_schema.AddToCartResponse)
def add_to_cart(
    cart_item: cart_schema.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == cart_item.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    cart_item_db = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id, Cart.book_id == cart_item.book_id)
        .first()
    )

    if cart_item_db:
        if cart_item_db.cart_amount >= book.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Only {book.quantity} copy/copies available.",
            )
        cart_item_db.cart_amount += 1
        db.commit()
        db.refresh(cart_item_db)
        return {"data": {"cart_amount": cart_item_db.cart_amount}, "message": "Book added to cart."}
    else:
        if book.quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add more. Only {book.quantity} copy/copies available.",
            )
        new_cart_item = Cart(
            user_id=current_user.id,
            book_id=cart_item.book_id,
            cart_amount=1,
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        return {"data": {"cart_amount": new_cart_item.cart_amount}, "message": "Book added to cart."}


@router.get("", response_model=cart_schema.GetCartResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    return {"data": cart_items, "message": "Cart items retrieved successfully."}
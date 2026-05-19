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


@router.post("/decrement", response_model=cart_schema.DecrementCartItemResponse)
def decrement_cart_item(
    cart_item: cart_schema.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_item_db = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id, Cart.book_id == cart_item.book_id)
        .first()
    )

    if not cart_item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in cart",
        )

    if cart_item_db.cart_amount > 1:
        cart_item_db.cart_amount -= 1
        db.commit()
        db.refresh(cart_item_db)
        return {"data": {"cart_amount": cart_item_db.cart_amount}, "message": "Book quantity decremented in cart."}
    else:
        return {"data": {"cart_amount": cart_item_db.cart_amount}, "message": "Book quantity cannot be less than 1."}


@router.delete("/remove", response_model=cart_schema.RemoveCartItemsResponse)
def remove_from_cart(
    cart_items_to_remove: cart_schema.RemoveCartItems,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted_count = 0
    for book_id in cart_items_to_remove.book_ids:
        cart_item_db = (
            db.query(Cart)
            .filter(Cart.user_id == current_user.id, Cart.book_id == book_id)
            .first()
        )
        if cart_item_db:
            db.delete(cart_item_db)
            deleted_count += 1

    if deleted_count > 0:
        db.commit()
        return {"data": {"deleted_count": deleted_count}, "message": f"{deleted_count} item(s) removed from cart."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching books found in cart to remove.",
        )


@router.get("", response_model=cart_schema.GetCartResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    return {"data": cart_items, "message": "Cart items retrieved successfully."}
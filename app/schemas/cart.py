from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from .book import BookResponse


class CartItemCreate(BaseModel):
    book_id: int


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    cart_amount: int
    created_at: datetime
    updated_at: Optional[datetime]
    book: BookResponse

    class Config:
        from_attributes = True


class AddToCartResponse(BaseModel):
    data: dict
    message: str


class GetCartResponse(BaseModel):
    data: list[CartItemResponse]
    message: str

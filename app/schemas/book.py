from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any
from datetime import datetime
from app.schemas.user import UserResponse

class BookBase(BaseModel):
    title: str
    condition: str = Field(..., pattern="^(new|like new|used|old)$")
    price: float
    quantity: int
    description: str
    location: str
    category: str
    images: Optional[List[str]] = Field(default=[], max_items=5)
    is_sold: bool = False

    @field_validator('condition')
    @classmethod
    def validate_condition(cls, v: str) -> str:
        v = v.lower()
        if v not in ["new", "like new", "used", "old"]:
            raise ValueError('Condition must be one of: new, like new, used, old')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed_categories = [
            "School", "+2 College", "Bachelor & Above", 
            "Novels & Fiction", "Religion & Spirituality", 
            "Self-Help", "Children's Books", "Others"
        ]
        if v not in allowed_categories:
            pass
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    condition: Optional[str] = Field(None, pattern="^(new|like new|used|old)$")
    price: Optional[float] = None
    quantity: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    images: Optional[List[str]] = Field(None, max_items=5)
    is_sold: Optional[bool] = None
    is_deleted: Optional[bool] = None

class BookResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    condition: str
    price: float
    quantity: int
    description: str
    location: str
    category: str
    images: Optional[List[str]] = []
    is_sold: bool
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: Optional[UserResponse] = None
    is_wishlisted: Optional[bool] = False

    class Config:
        from_attributes = True

    @field_validator('images', mode='after')
    @classmethod
    def format_image_urls(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return []

        base_url = "http://127.0.0.1:8000" # You can move this to config.py later

        formatted_images = []
        for img in v:
            if img.startswith("http"):
                formatted_images.append(img)
            elif img.startswith("/"):
                formatted_images.append(f"{base_url}{img}")
            else:
                formatted_images.append(f"{base_url}/{img}")
        return formatted_images

class BookListResponse(BaseModel):
    data: List[BookResponse]
    message: str

class BookSingleResponse(BaseModel):
    data: BookResponse
    message: str

class DeleteResponse(BaseModel):
    data: Any
    message: str
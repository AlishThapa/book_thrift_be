from pydantic import BaseModel

class WishlistToggleResponse(BaseModel):
    data: dict
    message: str

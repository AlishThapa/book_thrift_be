from pydantic import BaseModel
from typing import List, Optional
from app.schemas.book import BookResponse


class DashboardResponse(BaseModel):
    near_you: Optional[List[BookResponse]] = []
    picks_for_you: Optional[List[BookResponse]] = []
    just_dropped: Optional[List[BookResponse]] = []
    trending_this_month: Optional[List[BookResponse]] = []


class DashboardAPIResponse(BaseModel):
    data: DashboardResponse
    message: str
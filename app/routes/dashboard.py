from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import get_db
from app.auth import get_current_user_optional
from app.models.user import User
from app.models.book import Book
from app.models.wishlist import Wishlist
from app.schemas.dashboard import DashboardAPIResponse, DashboardResponse
from datetime import datetime, timedelta
from typing import Optional, List
import math

router = APIRouter(prefix="/api", tags=["dashboard"])

def get_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d

@router.get("/dashboard", response_model=DashboardAPIResponse)
def get_dashboard(
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    # Near You
    near_you_books = []
    if lat and lng:
        # Bounding box calculation
        radius_km = 10
        lat_change = radius_km / 111.32  # Degrees per km for latitude
        lng_change = radius_km / (111.32 * math.cos(math.radians(lat)))

        min_lat = lat - lat_change
        max_lat = lat + lat_change
        min_lng = lng - lng_change
        max_lng = lng + lng_change

        # Initial query with bounding box
        candidate_books = db.query(Book).filter(
            Book.is_deleted == False,
            Book.is_sold == False,
            Book.latitude.isnot(None),
            Book.longitude.isnot(None),
            Book.latitude.between(min_lat, max_lat),
            Book.longitude.between(min_lng, max_lng)
        ).all()

        # Precise filtering
        for book in candidate_books:
            distance = get_distance(lat, lng, book.latitude, book.longitude)
            if distance <= radius_km:
                near_you_books.append(book)

        near_you_books = near_you_books[:5]

    # Picks for you
    picks_for_you_books = []
    if current_user:
        # Get genres from user's wishlist
        wishlisted_books = db.query(Book).join(Wishlist).filter(Wishlist.user_id == current_user.id).all()
        if wishlisted_books:
            genres = {book.category for book in wishlisted_books}
            picks_for_you_books = db.query(Book).filter(
                Book.category.in_(genres),
                Book.is_deleted == False,
                Book.is_sold == False,
                Book.owner_id != current_user.id
            ).order_by(func.random()).limit(5).all()

    if not picks_for_you_books:
        # Fallback to random books if no user or no wishlist
        picks_for_you_books = db.query(Book).filter(Book.is_deleted == False, Book.is_sold == False).order_by(func.random()).limit(5).all()


    # Just Dropped
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    just_dropped_books = db.query(Book).filter(
        Book.created_at >= twenty_four_hours_ago,
        Book.is_deleted == False,
        Book.is_sold == False
    ).order_by(Book.created_at.desc()).limit(5).all()

    # Trending This Month
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trending_this_month_books = db.query(Book).join(Wishlist).filter(
        Wishlist.created_at >= thirty_days_ago,
        Book.is_deleted == False,
        Book.is_sold == False
    ).group_by(Book.id).order_by(func.count(Wishlist.book_id).desc()).limit(5).all()


    dashboard_response = DashboardResponse(
        near_you=near_you_books,
        picks_for_you=picks_for_you_books,
        just_dropped=just_dropped_books,
        trending_this_month=trending_this_month_books
    )

    return {
        "data": dashboard_response,
        "message": "Dashboard data fetched successfully"
    }
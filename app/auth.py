from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def create_access_token(data: dict):
    """
    Creates a permanent access token without an expiration (exp) claim.
    """
    to_encode = data.copy()
    # Ensure sub is present
    if "sub" not in to_encode:
         raise ValueError("Token data must contain 'sub' key (email)")

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            print("Debug: No email in token payload")
            raise credentials_exception
    except JWTError as e:
        print(f"Debug: JWT Decode error: {e}")
        raise credentials_exception
    
    # Fetch the user by email only first to see if they exist
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        print(f"Debug: No user found for email {email}")
        raise credentials_exception

    # Check if the token matches the one in DB.
    # If the DB has no token yet (newly created table), we might need to update it or ignore this check once.
    if user.access_token != token:
        print(f"Debug: Token mismatch for {email}")
        # To be safe during this transition, let's update the DB token if it's empty
        if not user.access_token:
            user.access_token = token
            db.commit()
            db.refresh(user)
        else:
            raise credentials_exception

    return user

def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.email == email).first()
    if user is None or user.access_token != token:
        return None

    return user

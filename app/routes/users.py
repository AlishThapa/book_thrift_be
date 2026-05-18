import hashlib
import base64
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.database import get_db
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse, UserUpdate,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, Token
)
from app.models.user import User as UserModel
from app.auth import create_access_token, get_current_user
from config import settings

router = APIRouter(prefix="/api", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash(password: str) -> str:
    digest = hashlib.sha256(password.encode()).digest()
    return base64.b64encode(digest).decode()

def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_prehash(plain_password), hashed_password)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    db_user = UserModel(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        user_type=user.user_type,
        location=user.location,
        institution=user.institution,
        class_name=user.class_name,
        semester=user.semester
    )

    # Generate initial permanent access token
    access_token = create_access_token(data={"sub": db_user.email})
    db_user.access_token = access_token

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "data": UserResponse.from_orm(db_user),
        "message": "User registered successfully"
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if the stored token is missing or expired
    should_generate_new = False
    if not db_user.access_token:
        should_generate_new = True
    else:
        try:
            # Check if current token is valid
            jwt.decode(db_user.access_token, settings.secret_key, algorithms=[settings.algorithm])
        except JWTError:
            # If expired or invalid, we need a new permanent one
            should_generate_new = True

    if should_generate_new:
        db_user.access_token = create_access_token(data={"sub": db_user.email})
        db.commit()
        db.refresh(db_user)

    return {
        "data": {"access_token": db_user.access_token, "token_type": "bearer"},
        "message": "Login successful"
    }

@router.get("/get-profile")
def get_profile(current_user: UserModel = Depends(get_current_user)):
    return {
        "data": UserResponse.from_orm(current_user),
        "message": "Profile fetched successfully"
    }

@router.put("/edit-profile")
def edit_profile(user_update: UserUpdate, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if email is being updated and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(UserModel).filter(UserModel.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return {
        "data": UserResponse.from_orm(current_user),
        "message": "Profile updated successfully"
    }

@router.delete("/delete-account")
def delete_account(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {
        "data": None,
        "message": "User account deleted successfully"
    }

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == request.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    return {
        "data": None,
        "message": "If your email is registered, you will receive a password reset link shortly."
    }

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == request.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db_user.password = hash_password(request.new_password)
    # When password is reset, we might want to keep the same token or refresh it
    # For now, we keep it as is.
    db.commit()
    return {
        "data": None,
        "message": "Password updated successfully"
    }

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(request.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid old password"
        )

    current_user.password = hash_password(request.new_password)
    db.commit()
    return {
        "data": None,
        "message": "Password changed successfully"
    }

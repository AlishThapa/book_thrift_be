from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
import re


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=12)
    phone: str = Field(..., min_length=10, max_length=15)
    user_type: str = Field(..., pattern="^(student|seller|both)$")
    location: str
    institution: str
    class_name: str
    semester: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6 or len(v) > 12:
            raise ValueError('Password must be between 6 and 12 characters')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least 1 number')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least 1 capital letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least 1 special character')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(v) < 10 or len(v) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    user_type: Optional[str] = Field(None, pattern="^(student|seller|both)$")
    location: Optional[str] = None
    institution: Optional[str] = None
    class_name: Optional[str] = None
    semester: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(v) < 10 or len(v) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(..., min_length=6, max_length=12)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6 or len(v) > 12:
            raise ValueError('Password must be between 6 and 12 characters')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least 1 number')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least 1 capital letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least 1 special character')
        return v


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=12)
    confirm_new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6 or len(v) > 12:
            raise ValueError('Password must be between 6 and 12 characters')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least 1 number')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least 1 capital letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least 1 special character')
        return v

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'ChangePasswordRequest':
        if self.new_password != self.confirm_new_password:
            raise ValueError('New passwords do not match')
        return self


class UserResponse(BaseModel):
    id: int
    uid: str
    full_name: str
    email: EmailStr
    phone: str
    user_type: str
    location: str
    institution: str
    class_name: str
    semester: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

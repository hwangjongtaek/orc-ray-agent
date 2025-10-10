"""
Pydantic schemas for User entity
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields"""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""

    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database"""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response (public view)"""

    pass


class Token(BaseModel):
    """Schema for authentication token response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class TokenData(BaseModel):
    """Schema for token payload data"""

    user_id: Optional[int] = None

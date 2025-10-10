"""
FastAPI dependency injection functions
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_db() -> Generator:
    """
    Dependency function to get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Get current user ID from JWT token.

    Args:
        token: JWT token from OAuth2 scheme

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid or missing user ID
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        return int(user_id)
    except ValueError:
        raise credentials_exception


async def get_current_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get current user from database.

    Args:
        db: Database session
        user_id: Current user ID from token

    Returns:
        User model instance

    Raises:
        HTTPException: If user not found or inactive
    """
    from app.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

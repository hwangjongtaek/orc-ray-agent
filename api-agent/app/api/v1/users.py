"""
TDD GREEN Phase: User management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.security import get_password_hash
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate

router = APIRouter()


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create new user.

    Registers a new user in the system.
    """
    # Check if user with this email already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    db_user = UserModel(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("", response_model=dict)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get list of users.

    Retrieve paginated list of all users. Requires authentication.
    """
    # Get total count
    total = db.query(UserModel).count()

    # Get paginated users
    users = db.query(UserModel).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": users,
    }


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get user by ID.

    Retrieve specific user information by user ID. Requires authentication.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

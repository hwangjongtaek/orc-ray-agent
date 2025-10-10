"""
TDD RED Phase: Tests for User model
These tests will fail until we implement the User model
"""

import pytest
from datetime import datetime


def test_user_model_creation(db_session):
    """Test that a User can be created with all required fields"""
    from app.models.user import User

    # Create a user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_123",
        full_name="Test User",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Assertions
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password_123"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert isinstance(user.created_at, datetime)


def test_user_email_must_be_unique(db_session):
    """Test that email must be unique"""
    from app.models.user import User
    from sqlalchemy.exc import IntegrityError

    # Create first user
    user1 = User(
        email="duplicate@example.com",
        hashed_password="pass1",
        full_name="User One",
    )
    db_session.add(user1)
    db_session.commit()

    # Try to create second user with same email
    user2 = User(
        email="duplicate@example.com",
        hashed_password="pass2",
        full_name="User Two",
    )
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_default_is_active_true(db_session):
    """Test that is_active defaults to True"""
    from app.models.user import User

    user = User(
        email="active@example.com",
        hashed_password="password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.is_active is True


def test_user_relationship_with_jobs(db_session):
    """Test that User has relationship with Job"""
    from app.models.user import User

    user = User(
        email="user_with_jobs@example.com",
        hashed_password="password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Should have jobs relationship (empty list initially)
    assert hasattr(user, "jobs")
    assert user.jobs == []

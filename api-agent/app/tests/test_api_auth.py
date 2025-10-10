"""
TDD RED Phase: Tests for authentication API endpoints
These tests will fail until we implement the auth endpoints
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    from app.models.user import User
    from app.core.security import get_password_hash

    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success(client, test_user):
    """Test successful login returns access token"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_wrong_password(client, test_user):
    """Test login with wrong password fails"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_nonexistent_user(client):
    """Test login with non-existent user fails"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nobody@example.com", "password": "password"},
    )

    assert response.status_code == 401


def test_get_current_user(client, test_user):
    """Test getting current user info with valid token"""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Then get user info
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert "hashed_password" not in data  # Should not expose password


def test_get_current_user_no_token(client):
    """Test getting current user without token fails"""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token fails"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )

    assert response.status_code == 401

"""
TDD RED Phase: Tests for user management API endpoints
These tests will fail until we implement the user endpoints
"""

import pytest


def test_create_user_success(client):
    """Test successful user creation"""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "full_name": "New User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data  # Should not expose password


def test_create_user_duplicate_email(client, test_user):
    """Test creating user with duplicate email fails"""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "testuser@example.com",  # Same as test_user
            "password": "password123",
            "full_name": "Duplicate User",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_create_user_invalid_email(client):
    """Test creating user with invalid email fails"""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 422  # Validation error


def test_create_user_short_password(client):
    """Test creating user with password less than 8 characters fails"""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "user@example.com",
            "password": "short",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 422  # Validation error


def test_create_user_minimal_fields(client):
    """Test creating user with only required fields"""
    response = client.post(
        "/api/v1/users",
        json={
            "email": "minimal@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "minimal@example.com"
    assert data["full_name"] is None


def test_get_users_list_requires_auth(client):
    """Test getting users list requires authentication"""
    response = client.get("/api/v1/users")

    assert response.status_code == 401


def test_get_users_list_with_auth(client, auth_headers):
    """Test authenticated user can get users list"""
    response = client.get("/api/v1/users", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_user_by_id(client, test_user, auth_headers):
    """Test getting specific user by ID"""
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_user_not_found(client, auth_headers):
    """Test getting non-existent user returns 404"""
    response = client.get("/api/v1/users/99999", headers=auth_headers)

    assert response.status_code == 404


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


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers with valid token"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

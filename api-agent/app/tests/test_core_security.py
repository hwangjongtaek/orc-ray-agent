"""
TDD RED Phase: Tests for security module
These tests will fail until we implement security functions
"""

import pytest
from datetime import datetime, timedelta


def test_password_hashing():
    """Test password can be hashed"""
    from app.core.security import get_password_hash

    password = "securepassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert len(hashed) > 0
    assert hashed.startswith("$2b$")  # bcrypt hash prefix


def test_password_verification_correct():
    """Test correct password verification"""
    from app.core.security import get_password_hash, verify_password

    password = "mypassword"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_password_verification_incorrect():
    """Test incorrect password verification"""
    from app.core.security import get_password_hash, verify_password

    password = "mypassword"
    wrong_password = "wrongpassword"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False


def test_create_access_token():
    """Test JWT access token creation"""
    from app.core.security import create_access_token

    data = {"sub": "user@example.com"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0
    # JWT has 3 parts separated by dots
    assert token.count(".") == 2


def test_create_access_token_with_expiration():
    """Test JWT token with custom expiration"""
    from app.core.security import create_access_token

    data = {"sub": "user@example.com"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires_delta)

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    """Test JWT token can be decoded"""
    from app.core.security import create_access_token, decode_access_token

    data = {"sub": "user@example.com", "role": "admin"}
    token = create_access_token(data)

    decoded = decode_access_token(token)

    assert decoded is not None
    assert decoded["sub"] == "user@example.com"
    assert decoded["role"] == "admin"
    assert "exp" in decoded


def test_decode_invalid_token():
    """Test decoding invalid token returns None"""
    from app.core.security import decode_access_token

    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)

    assert decoded is None


def test_decode_expired_token():
    """Test decoding expired token returns None"""
    from app.core.security import create_access_token, decode_access_token
    from time import sleep

    data = {"sub": "user@example.com"}
    # Create token that expires in 1 second
    expires_delta = timedelta(seconds=1)
    token = create_access_token(data, expires_delta=expires_delta)

    # Wait for token to expire
    sleep(2)

    decoded = decode_access_token(token)
    assert decoded is None

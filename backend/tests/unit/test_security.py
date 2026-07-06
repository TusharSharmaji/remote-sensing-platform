"""Unit tests for password hashing and JWT token utilities."""

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.exceptions import InvalidTokenException
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

settings = get_settings()


def test_hash_password_produces_different_value_than_plaintext() -> None:
    """Hashing should never return the original plaintext password."""
    hashed = hash_password("SuperSecret1")
    assert hashed != "SuperSecret1"


def test_verify_password_succeeds_with_correct_password() -> None:
    """Verification should succeed when the plaintext matches the hash."""
    hashed = hash_password("SuperSecret1")
    assert verify_password("SuperSecret1", hashed) is True


def test_verify_password_fails_with_incorrect_password() -> None:
    """Verification should fail when the plaintext does not match the hash."""
    hashed = hash_password("SuperSecret1")
    assert verify_password("WrongPassword1", hashed) is False


def test_create_access_token_has_correct_claims() -> None:
    """Access tokens should embed subject, role, and type claims correctly."""
    token = create_access_token(subject="user-123", role="USER")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "user-123"
    assert payload["role"] == "USER"
    assert payload["type"] == "access"


def test_create_refresh_token_has_correct_type() -> None:
    """Refresh tokens should be marked with type 'refresh'."""
    token = create_refresh_token(subject="user-123", role="ADMIN")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["type"] == "refresh"


def test_decode_token_succeeds_for_matching_type() -> None:
    """Decoding should succeed when the expected type matches the token's type."""
    token = create_access_token(subject="user-123", role="USER")
    payload = decode_token(token, expected_type=TokenType.ACCESS)
    assert payload["sub"] == "user-123"


def test_decode_token_rejects_wrong_type() -> None:
    """Decoding should reject a valid token used as the wrong type."""
    token = create_access_token(subject="user-123", role="USER")
    with pytest.raises(InvalidTokenException):
        decode_token(token, expected_type=TokenType.REFRESH)


def test_decode_token_rejects_malformed_token() -> None:
    """Decoding should reject a syntactically invalid token."""
    with pytest.raises(InvalidTokenException):
        decode_token("not-a-valid-token", expected_type=TokenType.ACCESS)

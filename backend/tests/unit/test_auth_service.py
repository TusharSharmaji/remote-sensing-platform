"""Unit tests for AuthService business logic using an in-memory fake repository."""

import uuid

import pytest

from app.core.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
)
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User, UserRole
from app.schemas.user import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


class FakeUserRepository:
    """In-memory stand-in for UserRepository used to isolate AuthService in unit tests."""

    def __init__(self) -> None:
        """Initialize an empty in-memory user store."""
        self._users: dict[uuid.UUID, User] = {}

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return the stored user with the given id, or None."""
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        """Return the stored user with the given email, or None."""
        return next((u for u in self._users.values() if u.email == email.lower()), None)

    def create(self, *, email: str, hashed_password: str, full_name: str) -> User:
        """Create and store a new fake user record."""
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.USER,
            is_active=True,
        )
        self._users[user.id] = user
        return user

    def exists_by_email(self, email: str) -> bool:
        """Return True if a user with the given email is already stored."""
        return self.get_by_email(email) is not None


@pytest.fixture()
def auth_service() -> AuthService:
    """Provide an AuthService backed by a fake in-memory repository."""
    return AuthService(FakeUserRepository())  # type: ignore[arg-type]


def test_register_creates_new_user(auth_service: AuthService) -> None:
    """Registering with a unique email should create a new user."""
    payload = RegisterRequest(email="new@example.com", password="Password1", full_name="New User")
    user = auth_service.register(payload)
    assert user.email == "new@example.com"
    assert user.hashed_password != "Password1"


def test_register_rejects_duplicate_email(auth_service: AuthService) -> None:
    """Registering the same email twice should raise UserAlreadyExistsException."""
    payload = RegisterRequest(email="dup@example.com", password="Password1", full_name="Dup User")
    auth_service.register(payload)
    with pytest.raises(UserAlreadyExistsException):
        auth_service.register(payload)


def test_authenticate_succeeds_with_correct_credentials(auth_service: AuthService) -> None:
    """Authenticating with correct credentials should return the matching user."""
    auth_service.register(
        RegisterRequest(email="login@example.com", password="Password1", full_name="Login User")
    )
    user = auth_service.authenticate(LoginRequest(email="login@example.com", password="Password1"))
    assert user.email == "login@example.com"


def test_authenticate_fails_with_wrong_password(auth_service: AuthService) -> None:
    """Authenticating with the wrong password should raise InvalidCredentialsException."""
    auth_service.register(
        RegisterRequest(email="login2@example.com", password="Password1", full_name="Login User")
    )
    with pytest.raises(InvalidCredentialsException):
        auth_service.authenticate(LoginRequest(email="login2@example.com", password="WrongPass1"))


def test_authenticate_fails_for_unknown_email(auth_service: AuthService) -> None:
    """Authenticating with an unregistered email should raise InvalidCredentialsException."""
    with pytest.raises(InvalidCredentialsException):
        auth_service.authenticate(LoginRequest(email="ghost@example.com", password="Password1"))


def test_authenticate_fails_for_inactive_user(auth_service: AuthService) -> None:
    """Authenticating as a deactivated user should raise InactiveUserException."""
    user = auth_service.register(
        RegisterRequest(email="inactive@example.com", password="Password1", full_name="Inactive")
    )
    user.is_active = False
    with pytest.raises(InactiveUserException):
        auth_service.authenticate(LoginRequest(email="inactive@example.com", password="Password1"))


def test_login_returns_token_pair(auth_service: AuthService) -> None:
    """A successful login should return both an access and a refresh token."""
    auth_service.register(
        RegisterRequest(email="tokens@example.com", password="Password1", full_name="Token User")
    )
    tokens = auth_service.login(LoginRequest(email="tokens@example.com", password="Password1"))
    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.token_type == "bearer"


def test_refresh_returns_new_token_pair(auth_service: AuthService) -> None:
    """A valid refresh token should yield a new access/refresh token pair."""
    user = auth_service.register(
        RegisterRequest(email="refresh@example.com", password="Password1", full_name="Refresh")
    )
    refresh_token = create_refresh_token(subject=str(user.id), role=user.role.value)
    tokens = auth_service.refresh(refresh_token)
    assert tokens.access_token
    assert tokens.refresh_token


def test_refresh_rejects_access_token(auth_service: AuthService) -> None:
    """Using an access token in place of a refresh token should be rejected."""
    user = auth_service.register(
        RegisterRequest(email="refresh2@example.com", password="Password1", full_name="Refresh")
    )
    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    with pytest.raises(InvalidTokenException):
        auth_service.refresh(access_token)

"""Authentication business logic: registration, login, and token lifecycle."""

import uuid

from app.core.exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenResponse
from app.schemas.user import LoginRequest, RegisterRequest


class AuthService:
    """Coordinates user registration, authentication, and JWT issuance."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Inject the repository this service depends on."""
        self._users = user_repository

    def register(self, payload: RegisterRequest) -> User:
        """Create a new user account after verifying the email is unused."""
        if self._users.exists_by_email(payload.email):
            raise UserAlreadyExistsException()
        hashed = hash_password(payload.password)
        return self._users.create(
            email=payload.email, hashed_password=hashed, full_name=payload.full_name
        )

    def authenticate(self, payload: LoginRequest) -> User:
        """Validate credentials and return the matching active user."""
        user = self._users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsException()
        if not user.is_active:
            raise InactiveUserException()
        return user

    def issue_tokens(self, user: User) -> TokenResponse:
        """Generate a fresh access/refresh token pair for the given user."""
        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id), role=user.role.value)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def login(self, payload: LoginRequest) -> TokenResponse:
        """Authenticate the user and issue a new token pair."""
        user = self.authenticate(payload)
        return self.issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        """Validate a refresh token and issue a new token pair for its owner."""
        payload = decode_token(refresh_token, expected_type=TokenType.REFRESH)
        subject = payload.get("sub")
        if subject is None:
            raise InvalidTokenException()

        user = self._users.get_by_id(uuid.UUID(subject))
        if user is None:
            raise UserNotFoundException()
        if not user.is_active:
            raise InactiveUserException()

        return self.issue_tokens(user)

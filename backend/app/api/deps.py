"""Shared FastAPI dependencies for authentication and role-based authorization."""

import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    InactiveUserException,
    InvalidTokenException,
    UserNotFoundException,
)
from app.core.security import TokenType, decode_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the currently authenticated user from a bearer access token."""
    payload = decode_token(token, expected_type=TokenType.ACCESS)
    subject = payload.get("sub")
    if subject is None:
        raise InvalidTokenException()

    repository = UserRepository(db)
    user = repository.get_by_id(uuid.UUID(subject))
    if user is None:
        raise UserNotFoundException()
    if not user.is_active:
        raise InactiveUserException()
    return user


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """Build a dependency that restricts access to the given set of roles."""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        """Ensure the current user's role is permitted, else raise 403."""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency

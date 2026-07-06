"""Data access layer for User entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Encapsulates all direct database access for the User model."""

    def __init__(self, db: Session) -> None:
        """Bind the repository to a SQLAlchemy session."""
        self._db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return the user with the given id, or None if not found."""
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email (case-insensitive), or None."""
        stmt = select(User).where(User.email == email.lower())
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, *, email: str, hashed_password: str, full_name: str) -> User:
        """Persist and return a new user record."""
        user = User(email=email.lower(), hashed_password=hashed_password, full_name=full_name)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def exists_by_email(self, email: str) -> bool:
        """Return True if a user with the given email already exists."""
        return self.get_by_email(email) is not None

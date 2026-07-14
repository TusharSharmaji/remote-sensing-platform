"""Domain-level exceptions mapped to HTTP responses by the global exception handler."""

from fastapi import status


class AppException(Exception):
    """Base class for all domain exceptions carrying an HTTP status code."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: str | None = None) -> None:
        """Initialize the exception, optionally overriding the default detail message."""
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class UserAlreadyExistsException(AppException):
    """Raised when attempting to register an email that is already in use."""

    status_code = status.HTTP_409_CONFLICT
    detail = "A user with this email already exists."


class InvalidCredentialsException(AppException):
    """Raised when login credentials do not match any active account."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect email or password."


class InactiveUserException(AppException):
    """Raised when an authenticated action is attempted by a deactivated user."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "This user account is inactive."


class InvalidTokenException(AppException):
    """Raised when a JWT is malformed, expired, or of the wrong type."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials."


class UserNotFoundException(AppException):
    """Raised when a referenced user id does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found."


class InsufficientPermissionsException(AppException):
    """Raised when a user's role does not permit the requested action."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "You do not have permission to perform this action."


class ProjectNotFoundException(AppException):
    """Raised when a referenced project id does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Project not found."


class ProjectAccessDeniedException(AppException):
    """Raised when a user attempts to access a project they do not own."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access denied."
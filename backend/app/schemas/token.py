"""Pydantic schemas for JWT token issuance and refresh."""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Access/refresh token pair returned after successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Payload required to exchange a refresh token for a new token pair."""

    refresh_token: str = Field(min_length=1)


class TokenPayload(BaseModel):
    """Decoded structure of a JWT's claims, used for internal validation."""

    sub: str
    role: str
    type: str
    exp: int

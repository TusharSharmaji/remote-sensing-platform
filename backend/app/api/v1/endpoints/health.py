"""Liveness and readiness health check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)
settings = get_settings()


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    """Return process liveness status without checking external dependencies."""
    return {"status": "ok", "environment": settings.environment}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Verify the database connection is reachable and return readiness status."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("readiness_check_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not available.",
        ) from exc
    return {"status": "ok", "database": "connected"}

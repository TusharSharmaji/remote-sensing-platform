"""Tests for liveness and readiness health endpoints."""

from fastapi.testclient import TestClient


def test_liveness_returns_ok(client: TestClient) -> None:
    """Liveness endpoint should return 200 with status ok."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_returns_ok_with_db(client: TestClient) -> None:
    """Readiness endpoint should return 200 when the database session works."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}

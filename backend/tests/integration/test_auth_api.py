"""Integration tests for authentication and user profile API endpoints."""

from fastapi.testclient import TestClient


def test_register_creates_user(client: TestClient) -> None:
    """POST /auth/register should create a user and return 201 with a public profile."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "Password1", "full_name": "Alice"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "USER"
    assert "hashed_password" not in body


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    """Registering the same email twice should return 409 Conflict."""
    payload = {"email": "bob@example.com", "password": "Password1", "full_name": "Bob"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_register_rejects_weak_password(client: TestClient) -> None:
    """Registering with a password lacking a digit should return 422."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "alllettersnodigits", "full_name": "Weak"},
    )
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client: TestClient) -> None:
    """POST /auth/login with correct credentials should return a token pair."""
    payload = {"email": "carol@example.com", "password": "Password1", "full_name": "Carol"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post(
        "/api/v1/auth/login", json={"email": "carol@example.com", "password": "Password1"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_fails_with_wrong_password(client: TestClient) -> None:
    """POST /auth/login with an incorrect password should return 401."""
    payload = {"email": "dave@example.com", "password": "Password1", "full_name": "Dave"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post(
        "/api/v1/auth/login", json={"email": "dave@example.com", "password": "WrongPass1"}
    )
    assert response.status_code == 401


def test_refresh_returns_new_access_token(client: TestClient) -> None:
    """POST /auth/refresh with a valid refresh token should return a new token pair."""
    payload = {"email": "erin@example.com", "password": "Password1", "full_name": "Erin"}
    client.post("/api/v1/auth/register", json=payload)
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "erin@example.com", "password": "Password1"}
    )
    refresh_token = login_response.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_rejects_access_token_as_refresh(client: TestClient) -> None:
    """POST /auth/refresh should reject an access token passed as a refresh token."""
    payload = {"email": "frank@example.com", "password": "Password1", "full_name": "Frank"}
    client.post("/api/v1/auth/register", json=payload)
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "frank@example.com", "password": "Password1"}
    )
    access_token = login_response.json()["access_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401


def test_get_current_user_requires_authentication(client: TestClient) -> None:
    """GET /users/me without a token should return 401."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_current_user_returns_profile_with_valid_token(client: TestClient) -> None:
    """GET /users/me with a valid access token should return the user's profile."""
    payload = {"email": "grace@example.com", "password": "Password1", "full_name": "Grace"}
    client.post("/api/v1/auth/register", json=payload)
    login_response = client.post(
        "/api/v1/auth/login", json={"email": "grace@example.com", "password": "Password1"}
    )
    access_token = login_response.json()["access_token"]
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "grace@example.com"


def test_get_current_user_rejects_invalid_token(client: TestClient) -> None:
    """GET /users/me with a malformed token should return 401."""
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401

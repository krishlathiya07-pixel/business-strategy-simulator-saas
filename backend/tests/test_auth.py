from fastapi.testclient import TestClient
from backend.app.core.config import settings

def test_register_user(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "test@example.com", "password": "testpassword", "full_name": "Test User"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_login_user(client: TestClient):
    # Register first
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "login@example.com", "password": "testpassword", "full_name": "Login User"},
    )
    # Login
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": "login@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

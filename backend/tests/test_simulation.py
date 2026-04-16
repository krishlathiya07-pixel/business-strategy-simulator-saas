import pytest
from fastapi.testclient import TestClient
from backend.app.core.config import settings

@pytest.fixture
def auth_token(client: TestClient):
    # Register and login to get token
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": "sim@example.com", "password": "testpassword", "full_name": "Sim User"},
    )
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": "sim@example.com", "password": "testpassword"},
    )
    return response.json()["access_token"]

def test_simulation_flow(client: TestClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get initial state
    response = client.get(f"{settings.API_V1_STR}/simulation/state", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "revenue" in data
    assert data["quarter"] == 0
    
    # Take a step
    response = client.post(
        f"{settings.API_V1_STR}/simulation/step",
        headers=headers,
        json={"action": "increase_marketing", "amount": 5000}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quarter"] == 1
    
    # Check history
    response = client.get(f"{settings.API_V1_STR}/simulation/history", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["history"]) == 1

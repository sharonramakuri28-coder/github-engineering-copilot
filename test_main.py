from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "GitHub Engineering Copilot is running"
    }


def test_login():
    response = client.post(
        "/auth/login",
        json={
            "username": "sharon",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_repo():
    response = client.get("/repos/tiangolo/fastapi")

    assert response.status_code == 200

    data = response.json()

    assert "name" in data
    assert "stars" in data


def test_pull_requests():
    response = client.get("/repos/tiangolo/fastapi/pulls")

    assert response.status_code == 200

    assert isinstance(response.json(), list)
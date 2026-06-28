import jwt
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_auth_app():
    response = client.post("api/app/auth",json=
        {
            "email":"thebackdoors182@gmail.com",
            "password":"test123!@#"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["csrf"] is None

    # Check token fields exist
    assert "access_token" in data["token"]
    assert "refresh_token" in data["token"]

def test_auth():
    response = client.post("api/auth", json={"email": "thebackdoors182@gmail.com", "password": "test123!@#"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["csrf"] is not None

    assert "access_token" not in data["token"]
    assert "refresh_token" not in data["token"]

    cookies = response.cookies

    assert "access_token" in cookies
    assert "refresh_token" in cookies
    assert "csrf_token" in cookies

    assert cookies.get("access_token") != cookies.get("refresh_token")

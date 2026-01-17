import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_user(client, test_user):
    """Test registering duplicate user"""
    response = client.post(
        "/api/v1/users/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_user(client, test_user):
    """Test user login"""
    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/users/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    """Test getting current user without auth"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



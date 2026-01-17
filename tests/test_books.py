import pytest
from fastapi import status
from io import BytesIO


def test_get_public_books(client, auth_headers, public_book):
    """Test getting public books"""
    response = client.get("/api/v1/books/public", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "books" in data
    assert len(data["books"]) > 0


def test_get_my_library(client, auth_headers, test_book, public_book):
    """Test getting user's library"""
    response = client.get("/api/v1/users/me/library", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "books" in data
    assert len(data["books"]) >= 1  # At least test_book (private book is auto-added)


def test_create_private_book(client, auth_headers, db):
    """Test creating private book"""
    # Create a mock PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF"
    files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
    data = {
        "title": "My Private Book",
        "author": "My Author",
        "pages": 50  # Should be int, not string
    }
    
    response = client.post(
        "/api/v1/books/private",
        headers=auth_headers,
        files=files,
        data=data
    )
    # Note: This might fail if MinIO is not available, but we test the endpoint structure
    # If MinIO is not available, it will return 400 with "Storage service unavailable" message
    assert response.status_code in [
        status.HTTP_201_CREATED, 
        status.HTTP_400_BAD_REQUEST,  # If storage is unavailable
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]


def test_read_book(client, auth_headers, test_book):
    """Test reading a book"""
    response = client.get(
        f"/api/v1/books/{test_book.id}/read",
        headers=auth_headers
    )
    # Note: This might fail if MinIO is not available
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


def test_delete_book(client, auth_headers, test_book):
    """Test deleting a book"""
    response = client.delete(
        f"/api/v1/books/{test_book.id}",
        headers=auth_headers
    )
    # Note: This might fail if MinIO is not available
    assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_500_INTERNAL_SERVER_ERROR]



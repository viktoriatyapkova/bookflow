import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock


@patch('app.integrations.application.google_books_service.GoogleBooksService.search_books')
def test_search_books(mock_search, client, auth_headers):
    """Test searching books via Google Books API"""
    mock_search.return_value = [
        {
            "title": "Test Book",
            "author": "Test Author",
            "pages": 100,
            "description": "Test description",
            "published_date": "2024",
            "isbn": "1234567890",
            "thumbnail": "http://example.com/thumb.jpg"
        }
    ]
    
    response = client.get(
        "/api/v1/integrations/google-books/search?query=test",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "books" in data
    assert len(data["books"]) > 0


@patch('app.integrations.application.google_books_service.GoogleBooksService.get_book_by_isbn')
def test_get_book_by_isbn(mock_get, client, auth_headers):
    """Test getting book by ISBN via Google Books API"""
    mock_get.return_value = {
        "title": "Test Book",
        "author": "Test Author",
        "pages": 100,
        "description": "Test description",
        "published_date": "2024",
        "isbn": "1234567890",
        "thumbnail": "http://example.com/thumb.jpg"
    }
    
    response = client.get(
        "/api/v1/integrations/google-books/isbn/1234567890",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Book"



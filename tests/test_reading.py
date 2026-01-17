import pytest
from fastapi import status


def test_update_progress(client, auth_headers, test_book):
    """Test updating reading progress"""
    response = client.put(
        f"/api/v1/reading/progress/{test_book.id}",
        headers=auth_headers,
        json={"current_page": 25}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["current_page"] == 25
    assert "progress_percentage" in data


def test_get_progress(client, auth_headers, test_book, db):
    """Test getting reading progress"""
    from app.reading.infrastructure.reading_repository import ReadingRepository
    from app.reading.domain.models import ReadingProgress
    import uuid
    
    # Create progress first
    reading_repository = ReadingRepository()
    progress = ReadingProgress(
        id=uuid.uuid4(),
        user_id=test_book.owner_id,
        book_id=test_book.id,
        current_page=30
    )
    reading_repository.create_progress(db, progress)
    
    response = client.get(
        f"/api/v1/reading/progress/{test_book.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["current_page"] == 30


def test_get_habit(client, auth_headers, db):
    """Test getting reading habit"""
    response = client.get("/api/v1/reading/habit", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "daily_goal_pages" in data
    assert "current_streak" in data


def test_update_habit(client, auth_headers):
    """Test updating reading habit"""
    response = client.put(
        "/api/v1/reading/habit",
        headers=auth_headers,
        json={"daily_goal_pages": 20}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["daily_goal_pages"] == 20


def test_get_stats(client, auth_headers):
    """Test getting reading statistics"""
    response = client.get("/api/v1/reading/stats", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_books_read" in data
    assert "total_pages_read" in data
    assert "current_streak" in data
    assert "daily_goal_pages" in data



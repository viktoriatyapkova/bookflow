import pytest
import uuid
from app.users.domain.models import User
from app.books.domain.models import Book, BookStatus
from app.reading.domain.models import ReadingProgress, ReadingHabit


def test_user_model():
    """Test User domain model"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password="hashed_password"
    )
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"


def test_book_model():
    """Test Book domain model"""
    book = Book(
        id=uuid.uuid4(),
        title="Test Book",
        author="Test Author",
        pages=100,
        is_public=False,
        owner_id=uuid.uuid4(),
        file_path="test/path.pdf"
    )
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.pages == 100
    assert book.is_public is False


def test_reading_progress_model():
    """Test ReadingProgress domain model"""
    progress = ReadingProgress(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        book_id=uuid.uuid4(),
        current_page=25
    )
    assert progress.current_page == 25


def test_reading_habit_model():
    """Test ReadingHabit domain model"""
    habit = ReadingHabit(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        daily_goal_pages=10,
        current_streak=5
    )
    assert habit.daily_goal_pages == 10
    assert habit.current_streak == 5


def test_book_status_enum():
    """Test BookStatus enum"""
    assert BookStatus.PLANNED == "planned"
    assert BookStatus.READING == "reading"
    assert BookStatus.FINISHED == "finished"



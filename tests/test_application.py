import pytest
import uuid
from app.users.application.user_service import UserService
from app.users.application.auth_service import AuthService
from app.users.infrastructure.user_repository import UserRepository
from app.books.application.book_service import BookService
from app.books.infrastructure.book_repository import BookRepository
from app.reading.application.reading_service import ReadingService
from app.reading.infrastructure.reading_repository import ReadingRepository


def test_auth_service_password_hashing():
    """Test password hashing"""
    user_repository = UserRepository()
    auth_service = AuthService(user_repository)
    
    password = "testpassword"
    hashed = auth_service.get_password_hash(password)
    
    assert hashed != password
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("wrongpassword", hashed)


def test_auth_service_create_token():
    """Test JWT token creation"""
    user_repository = UserRepository()
    auth_service = AuthService(user_repository)
    
    user_id = str(uuid.uuid4())
    token = auth_service.create_access_token({"sub": user_id})
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded_id = auth_service.get_current_user_id(token)
    assert decoded_id == user_id


def test_user_service_create_user(db):
    """Test user creation"""
    user_repository = UserRepository()
    auth_service = AuthService(user_repository)
    user_service = UserService(user_repository, auth_service)
    
    user = user_service.create_user(
        db,
        "newuser@example.com",
        "password123"
    )
    
    assert user.email == "newuser@example.com"
    assert user.hashed_password != "password123"
    
    # Test duplicate user
    with pytest.raises(ValueError):
        user_service.create_user(
            db,
            "newuser@example.com",
            "password123"
        )


def test_book_service_get_public_books(db, public_book):
    """Test getting public books"""
    book_repository = BookRepository()
    book_service = BookService(book_repository)
    
    books = book_service.get_public_books(db)
    assert len(books) > 0
    assert all(book.is_public for book in books)


def test_reading_service_update_progress(db, test_user, test_book):
    """Test updating reading progress"""
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    progress = reading_service.update_progress(
        db,
        test_user.id,
        test_book.id,
        25
    )
    
    assert progress.current_page == 25
    assert progress.user_id == test_user.id
    assert progress.book_id == test_book.id


def test_reading_service_get_progress_percentage(db, test_user, test_book):
    """Test getting progress percentage"""
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    reading_service.update_progress(db, test_user.id, test_book.id, 50)
    percentage = reading_service.get_progress_percentage(
        db, test_user.id, test_book.id
    )
    
    assert percentage == 50.0  # 50 pages out of 100



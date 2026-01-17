import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

from app.infrastructure.database import Base, get_db
from app.main import app
from app.users.domain.models import User
from app.books.domain.models import Book
from app.reading.domain.models import ReadingProgress, ReadingHabit
from app.users.application.auth_service import AuthService
from app.users.infrastructure.user_repository import UserRepository

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create test user"""
    user_repository = UserRepository()
    auth_service = AuthService(user_repository)
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=auth_service.get_password_hash("testpassword")
    )
    return user_repository.create(db, user)


@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for test user"""
    response = client.post(
        "/api/v1/users/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_book(db, test_user):
    """Create test book and add it to user's library"""
    from app.books.infrastructure.book_repository import BookRepository
    from app.books.infrastructure.user_book_repository import UserBookRepository
    from app.books.domain.models import UserBook, BookStatus
    
    book = Book(
        id=uuid.uuid4(),
        title="Test Book",
        author="Test Author",
        pages=100,
        is_public=False,
        owner_id=test_user.id,
        file_path="test/path.pdf"
    )
    book_repository = BookRepository()
    book = book_repository.create(db, book)
    
    # Add book to user's library (as private books are auto-added)
    user_book_repository = UserBookRepository()
    user_book = UserBook(
        id=uuid.uuid4(),
        user_id=test_user.id,
        book_id=book.id,
        status=BookStatus.PLANNED
    )
    user_book_repository.create(db, user_book)
    
    return book


@pytest.fixture
def public_book(db):
    """Create public test book"""
    from app.books.infrastructure.book_repository import BookRepository
    
    book = Book(
        id=uuid.uuid4(),
        title="Public Book",
        author="Public Author",
        pages=200,
        is_public=True,
        owner_id=None,
        file_path="public/path.pdf"
    )
    book_repository = BookRepository()
    return book_repository.create(db, book)



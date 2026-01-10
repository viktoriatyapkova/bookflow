from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.books.domain.models import Book, UserBook, BookStatus
from app.books.infrastructure.book_repository import BookRepository
from app.books.infrastructure.user_book_repository import UserBookRepository
from app.integrations.application.google_books_service import GoogleBooksService


class LibraryService:
    def __init__(
        self,
        book_repository: BookRepository,
        user_book_repository: UserBookRepository
    ):
        self.book_repository = book_repository
        self.user_book_repository = user_book_repository

    async def add_book_by_isbn(
        self,
        db: Session,
        user_id: uuid.UUID,
        isbn: str,
        status: BookStatus = BookStatus.PLANNED
    ) -> UserBook:
        """Add book to user's library by ISBN"""
        # Check if book already exists in system by ISBN
        book = self.book_repository.get_by_isbn(db, isbn)
        
        if not book:
            # Fetch book data from Google Books API
            google_books_service = GoogleBooksService()
            book_data = await google_books_service.get_book_by_isbn(isbn)
            await google_books_service.close()
            
            if not book_data:
                raise ValueError(f"Book with ISBN {isbn} not found")
            
            # Create book in system (without PDF)
            book = Book(
                id=uuid.uuid4(),
                title=book_data["title"],
                author=book_data["author"],
                pages=book_data["pages"] or 0,
                isbn=isbn,
                is_public=False,
                owner_id=None,
                file_path=None  # No PDF file
            )
            book = self.book_repository.create(db, book)
        
        # Check if book already in user's library
        existing_user_book = self.user_book_repository.get_by_user_and_book(
            db, user_id, book.id
        )
        if existing_user_book:
            raise ValueError("Book already in your library")
        
        # Add to user's library
        user_book = UserBook(
            id=uuid.uuid4(),
            user_id=user_id,
            book_id=book.id,
            status=status
        )
        return self.user_book_repository.create(db, user_book)

    def add_public_book_to_library(
        self,
        db: Session,
        user_id: uuid.UUID,
        book_id: uuid.UUID,
        status: BookStatus = BookStatus.PLANNED
    ) -> UserBook:
        """Add public book to user's library"""
        # Check if book exists and is public
        book = self.book_repository.get_by_id(db, book_id)
        if not book:
            raise ValueError("Book not found")
        
        if not book.is_public:
            raise ValueError("Book is not public")
        
        # Check if already in library
        existing_user_book = self.user_book_repository.get_by_user_and_book(
            db, user_id, book_id
        )
        if existing_user_book:
            raise ValueError("Book already in your library")
        
        # Add to library
        user_book = UserBook(
            id=uuid.uuid4(),
            user_id=user_id,
            book_id=book_id,
            status=status
        )
        return self.user_book_repository.create(db, user_book)

    def get_user_library(
        self,
        db: Session,
        user_id: uuid.UUID,
        status: Optional[BookStatus] = None
    ) -> List[UserBook]:
        """Get user's library, optionally filtered by status"""
        return self.user_book_repository.get_user_library(db, user_id, status)

    def update_book_status(
        self,
        db: Session,
        user_id: uuid.UUID,
        book_id: uuid.UUID,
        status: BookStatus
    ) -> UserBook:
        """Update book status in user's library"""
        user_book = self.user_book_repository.update_status(
            db, user_id, book_id, status
        )
        if not user_book:
            raise ValueError("Book not found in your library")
        return user_book

    def remove_from_library(
        self,
        db: Session,
        user_id: uuid.UUID,
        book_id: uuid.UUID
    ) -> bool:
        """Remove book from user's library"""
        return self.user_book_repository.remove_from_library(db, user_id, book_id)



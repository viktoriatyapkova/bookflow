from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from fastapi import UploadFile

from app.books.domain.models import Book, UserBook, BookStatus
from app.books.infrastructure.book_repository import BookRepository
from app.infrastructure.storage import storage_service


class BookService:
    def __init__(self, book_repository: BookRepository, user_book_repository=None):
        self.book_repository = book_repository
        self.user_book_repository = user_book_repository

    async def create_public_book(
        self,
        db: Session,
        title: str,
        author: str,
        pages: int,
        file: UploadFile
    ) -> Book:
        """Create public book (admin only in real app, here simplified)"""
        # Upload file
        file_path = f"public/{uuid.uuid4()}.pdf"
        try:
            await storage_service.upload_file(file, file_path)
        except ConnectionError as e:
            raise ValueError(f"Storage service unavailable: {str(e)}")

        book = Book(
            id=uuid.uuid4(),
            title=title,
            author=author,
            pages=pages,
            isbn=None,
            is_public=True,
            owner_id=None,
            file_path=file_path
        )
        return self.book_repository.create(db, book)

    async def create_private_book(
        self,
        db: Session,
        title: str,
        author: str,
        pages: int,
        file: UploadFile,
        owner_id: uuid.UUID
    ) -> Book:
        """Create private book for user"""
        # Validate file
        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are allowed")
        
        # Check file size (20 MB max)
        file_content = await file.read()
        if len(file_content) > 20 * 1024 * 1024:
            raise ValueError("File size exceeds 20 MB limit")
        
        # Reset file pointer
        file.file.seek(0)

        # Upload file
        file_path = f"private/{owner_id}/{uuid.uuid4()}.pdf"
        try:
            await storage_service.upload_file(file, file_path)
        except ConnectionError as e:
            raise ValueError(f"Storage service unavailable: {str(e)}")

        book = Book(
            id=uuid.uuid4(),
            title=title,
            author=author,
            pages=pages,
            isbn=None,
            is_public=False,
            owner_id=owner_id,
            file_path=file_path
        )
        book = self.book_repository.create(db, book)
        
        # Automatically add private book to user's library
        if self.user_book_repository:
            from app.books.domain.models import UserBook, BookStatus
            existing_user_book = self.user_book_repository.get_by_user_and_book(
                db, owner_id, book.id
            )
            if not existing_user_book:
                user_book = UserBook(
                    id=uuid.uuid4(),
                    user_id=owner_id,
                    book_id=book.id,
                    status=BookStatus.PLANNED
                )
                self.user_book_repository.create(db, user_book)
        
        return book

    def get_public_books(self, db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get all public books"""
        return self.book_repository.get_public_books(db, skip=skip, limit=limit)

    def get_user_books(self, db: Session, user_id: uuid.UUID) -> List[Book]:
        """Get all books for user (private + public)"""
        return self.book_repository.get_user_books(db, user_id)

    def get_book_by_id(self, db: Session, book_id: uuid.UUID) -> Optional[Book]:
        """Get book by ID"""
        return self.book_repository.get_by_id(db, book_id)

    def delete_book(self, db: Session, book_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete private book (only owner can delete)"""
        book = self.book_repository.get_by_id(db, book_id)
        if not book:
            return False
        
        if book.is_public:
            raise ValueError("Cannot delete public books")
        
        if book.owner_id != user_id:
            raise ValueError("Only book owner can delete the book")
        
        # Delete file from storage
        storage_service.delete_file(book.file_path)
        
        # Delete book
        self.book_repository.delete(db, book_id)
        return True

    def get_book_file_stream(self, db: Session, book_id: uuid.UUID) -> Optional[bytes]:
        """Get book file as binary content"""
        try:
            book = self.book_repository.get_by_id(db, book_id)
            if not book:
                return None
            
            if not book.file_path:
                return None  # Book has no PDF file
            
            # Get file as binary bytes directly
            stream = storage_service.get_file_stream(book.file_path)
            if stream:
                # Read all bytes from BytesIO stream
                stream.seek(0)  # Reset to beginning
                return stream.read()
            return None
        except Exception as e:
            # Log error (in production use proper logging)
            print(f"Error reading file for book {book_id}: {str(e)}")
            return None


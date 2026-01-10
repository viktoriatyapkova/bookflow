from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.books.domain.models import UserBook, BookStatus


class UserBookRepository:
    def create(self, db: Session, user_book: UserBook) -> UserBook:
        """Create user book relationship"""
        db.add(user_book)
        db.commit()
        db.refresh(user_book)
        return user_book

    def get_by_user_and_book(
        self, db: Session, user_id: uuid.UUID, book_id: uuid.UUID
    ) -> Optional[UserBook]:
        """Get user book by user and book IDs"""
        return db.query(UserBook).filter(
            UserBook.user_id == user_id,
            UserBook.book_id == book_id
        ).first()

    def get_user_library(
        self, db: Session, user_id: uuid.UUID, status: Optional[BookStatus] = None
    ) -> List[UserBook]:
        """Get user's library books, optionally filtered by status"""
        query = db.query(UserBook).filter(UserBook.user_id == user_id)
        if status:
            query = query.filter(UserBook.status == status)
        return query.all()

    def update_status(
        self, db: Session, user_id: uuid.UUID, book_id: uuid.UUID, status: BookStatus
    ) -> Optional[UserBook]:
        """Update book status in user's library"""
        user_book = self.get_by_user_and_book(db, user_id, book_id)
        if user_book:
            user_book.status = status
            db.commit()
            db.refresh(user_book)
        return user_book

    def remove_from_library(
        self, db: Session, user_id: uuid.UUID, book_id: uuid.UUID
    ) -> bool:
        """Remove book from user's library"""
        user_book = self.get_by_user_and_book(db, user_id, book_id)
        if user_book:
            db.delete(user_book)
            db.commit()
            return True
        return False



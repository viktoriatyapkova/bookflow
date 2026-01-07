from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.books.domain.models import Book


class BookRepository:
    def create(self, db: Session, book: Book) -> Book:
        """Create book"""
        db.add(book)
        db.commit()
        db.refresh(book)
        return book

    def get_by_id(self, db: Session, book_id: uuid.UUID) -> Optional[Book]:
        """Get book by ID"""
        return db.query(Book).filter(Book.id == book_id).first()

    def get_public_books(self, db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get all public books"""
        return db.query(Book).filter(Book.is_public == True).offset(skip).limit(limit).all()

    def get_by_isbn(self, db: Session, isbn: str) -> Optional[Book]:
        """Get book by ISBN"""
        return db.query(Book).filter(Book.isbn == isbn).first()

    def get_user_books(self, db: Session, user_id: uuid.UUID) -> List[Book]:
        """Get all books accessible to user (private owned + public)"""
        return db.query(Book).filter(
            (Book.owner_id == user_id) | (Book.is_public == True)
        ).all()

    def delete(self, db: Session, book_id: uuid.UUID) -> bool:
        """Delete book"""
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            db.delete(book)
            db.commit()
            return True
        return False


from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.infrastructure.database import Base
from app.infrastructure.types import GUID


class BookStatus(str, enum.Enum):
    PLANNED = "planned"
    READING = "reading"
    FINISHED = "finished"


class Book(Base):
    __tablename__ = "books"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    isbn = Column(String, nullable=True, unique=True, index=True)
    is_public = Column(Boolean, default=False, nullable=False)
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    file_path = Column(String, nullable=True)  # Optional - can be None if book added by ISBN
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])


class UserBook(Base):
    __tablename__ = "user_books"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    book_id = Column(GUID(), ForeignKey("books.id"), nullable=False)
    status = Column(SQLEnum(BookStatus), default=BookStatus.PLANNED, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    book = relationship("Book", foreign_keys=[book_id])

    # Unique constraint: one book can be added to user's library only once
    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='uq_user_book'),
    )


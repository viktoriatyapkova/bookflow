from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.books.domain.models import BookStatus


class BookCreate(BaseModel):
    title: str
    author: str
    pages: int


class BookResponse(BaseModel):
    id: UUID
    title: str
    author: str
    pages: int
    isbn: Optional[str]
    is_public: bool
    owner_id: Optional[UUID]
    file_path: Optional[str]  # None if book added by ISBN without PDF
    has_pdf: bool  # Computed field
    created_at: datetime

    class Config:
        from_attributes = True


class UserBookResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    status: BookStatus
    added_at: datetime
    book: BookResponse  # Include book details

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    books: list[BookResponse]
    total: int


class UserLibraryResponse(BaseModel):
    books: list[UserBookResponse]
    total: int


class AddBookByISBNRequest(BaseModel):
    isbn: str
    status: BookStatus = BookStatus.PLANNED


class AddPublicBookRequest(BaseModel):
    book_id: UUID
    status: BookStatus = BookStatus.PLANNED


class UpdateBookStatusRequest(BaseModel):
    status: BookStatus


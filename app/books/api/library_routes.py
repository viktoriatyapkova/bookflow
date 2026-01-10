from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.infrastructure.database import get_db
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User
from app.books.api.schemas import (
    UserLibraryResponse,
    UserBookResponse,
    AddBookByISBNRequest,
    AddPublicBookRequest,
    UpdateBookStatusRequest,
    BookResponse
)
from app.books.application.library_service import LibraryService
from app.books.infrastructure.book_repository import BookRepository
from app.books.infrastructure.user_book_repository import UserBookRepository
from app.books.domain.models import BookStatus

router = APIRouter(prefix="/users/me/library", tags=["library"])


@router.post("/isbn", response_model=UserBookResponse, status_code=status.HTTP_201_CREATED)
async def add_book_by_isbn(
    request: AddBookByISBNRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add book to library by ISBN (without PDF)"""
    book_repository = BookRepository()
    user_book_repository = UserBookRepository()
    library_service = LibraryService(book_repository, user_book_repository)
    
    try:
        user_book = await library_service.add_book_by_isbn(
            db, current_user.id, request.isbn, request.status
        )
        # Load book relationship
        db.refresh(user_book)
        return _format_user_book_response(user_book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/public", response_model=UserBookResponse, status_code=status.HTTP_201_CREATED)
async def add_public_book(
    request: AddPublicBookRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add public book to library"""
    book_repository = BookRepository()
    user_book_repository = UserBookRepository()
    library_service = LibraryService(book_repository, user_book_repository)
    
    try:
        user_book = library_service.add_public_book_to_library(
            db, current_user.id, request.book_id, request.status
        )
        db.refresh(user_book)
        return _format_user_book_response(user_book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=UserLibraryResponse)
async def get_my_library(
    status: Optional[BookStatus] = Query(
        None,
        description="Filter by book status",
        examples=["planned", "reading", "finished"]
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's library, optionally filtered by status"""
    book_repository = BookRepository()
    user_book_repository = UserBookRepository()
    library_service = LibraryService(book_repository, user_book_repository)
    
    user_books = library_service.get_user_library(db, current_user.id, status)
    return UserLibraryResponse(
        books=[_format_user_book_response(ub) for ub in user_books],
        total=len(user_books)
    )


@router.put("/{book_id}/status", response_model=UserBookResponse)
async def update_book_status(
    book_id: str,
    request: UpdateBookStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update book status in library"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID")
    
    book_repository = BookRepository()
    user_book_repository = UserBookRepository()
    library_service = LibraryService(book_repository, user_book_repository)
    
    try:
        user_book = library_service.update_book_status(
            db, current_user.id, book_uuid, request.status
        )
        db.refresh(user_book)
        return _format_user_book_response(user_book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_library(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove book from library"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID")
    
    book_repository = BookRepository()
    user_book_repository = UserBookRepository()
    library_service = LibraryService(book_repository, user_book_repository)
    
    success = library_service.remove_from_library(db, current_user.id, book_uuid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found in library")


def _format_user_book_response(user_book: "UserBook") -> UserBookResponse:
    """Format UserBook with book details"""
    book = user_book.book
    book_response = BookResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        pages=book.pages,
        isbn=book.isbn,
        is_public=book.is_public,
        owner_id=book.owner_id,
        file_path=book.file_path,
        has_pdf=book.file_path is not None,
        created_at=book.created_at
    )
    
    return UserBookResponse(
        id=user_book.id,
        user_id=user_book.user_id,
        book_id=user_book.book_id,
        status=user_book.status,
        added_at=user_book.added_at,
        book=book_response
    )


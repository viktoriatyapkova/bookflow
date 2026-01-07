from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.infrastructure.database import get_db
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User
from app.books.api.schemas import BookResponse, BookListResponse
from app.books.domain.models import Book
from app.books.application.book_service import BookService
from app.books.infrastructure.book_repository import BookRepository

router = APIRouter(prefix="/books", tags=["books"])


def _format_book_response(book: Book) -> BookResponse:
    """Format Book response with computed fields"""
    return BookResponse(
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


@router.post("/public", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_public_book(
    title: str = Form(...),
    author: str = Form(...),
    pages: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create public book (simplified - in production should be admin only)"""
    book_repository = BookRepository()
    book_service = BookService(book_repository, None)
    
    try:
        book = await book_service.create_public_book(db, title, author, pages, file)
        return _format_book_response(book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/private", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_private_book(
    title: str = Form(...),
    author: str = Form(...),
    pages: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create private book (automatically added to library)"""
    from app.books.infrastructure.user_book_repository import UserBookRepository
    
    book_repository = BookRepository()
    user_book_repository = UserBookRepository()
    book_service = BookService(book_repository, user_book_repository)
    
    try:
        book = await book_service.create_private_book(
            db, title, author, pages, file, current_user.id
        )
        return _format_book_response(book)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/public", response_model=BookListResponse)
async def get_public_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all public books"""
    book_repository = BookRepository()
    book_service = BookService(book_repository, None)
    
    books = book_service.get_public_books(db, skip=skip, limit=limit)
    return BookListResponse(
        books=[_format_book_response(book) for book in books],
        total=len(books)
    )




@router.get("/{book_id}/read", response_class=StreamingResponse)
async def read_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stream PDF book for reading"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID")
    
    book_repository = BookRepository()
    book_service = BookService(book_repository, None)
    
    # Check if user has access to book
    book = book_service.get_book_by_id(db, book_uuid)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    if not book.is_public and book.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Check if book has PDF
    if not book.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This book has no PDF file. It was added by ISBN without file."
        )
    
    # Get file stream
    try:
        file_content = book_service.get_book_file_stream(db, book_uuid)
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book file not found in storage"
            )
        
        # Ensure file_content is bytes
        if isinstance(file_content, str):
            file_content = file_content.encode('utf-8')
        
        # Create response with proper binary content
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{book.title}.pdf"',
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading book file: {str(e)}"
        )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete private book"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID")
    
    book_repository = BookRepository()
    book_service = BookService(book_repository, None)
    
    try:
        book_service.delete_book(db, book_uuid, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User
from app.integrations.api.schemas import BookSearchResult, BookSearchResponse
from app.integrations.application.google_books_service import GoogleBooksService

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/google-books/search", response_model=BookSearchResponse)
async def search_books(
    query: str = Query(..., description="Search query (title, author, etc.)"),
    max_results: int = Query(10, ge=1, le=40, description="Maximum number of results"),
    current_user: User = Depends(get_current_user)
):
    """Search books using Google Books API"""
    service = GoogleBooksService()
    try:
        books_data = await service.search_books(query, max_results)
        books = [BookSearchResult(**book) for book in books_data]
        return BookSearchResponse(books=books, total=len(books))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching books: {str(e)}"
        )
    finally:
        await service.close()


@router.get("/google-books/isbn/{isbn}", response_model=BookSearchResult)
async def get_book_by_isbn(
    isbn: str,
    current_user: User = Depends(get_current_user)
):
    """Get book by ISBN using Google Books API"""
    service = GoogleBooksService()
    try:
        book_data = await service.get_book_by_isbn(isbn)
        if not book_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return BookSearchResult(**book_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching book: {str(e)}"
        )
    finally:
        await service.close()



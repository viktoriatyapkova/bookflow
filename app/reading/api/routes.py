from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.users.api.dependencies import get_current_user
from app.users.domain.models import User
from app.reading.api.schemas import (
    ReadingProgressUpdate,
    ReadingProgressResponse,
    ReadingHabitResponse,
    ReadingHabitUpdate,
    ReadingStatsResponse
)
from app.reading.application.reading_service import ReadingService
from app.reading.infrastructure.reading_repository import ReadingRepository
from app.books.infrastructure.book_repository import BookRepository

router = APIRouter(prefix="/reading", tags=["reading"])


@router.put("/progress/{book_id}", response_model=ReadingProgressResponse)
async def update_progress(
    book_id: str,
    progress_data: ReadingProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update reading progress"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID")
    
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    try:
        progress = reading_service.update_progress(
            db, current_user.id, book_uuid, progress_data.current_page
        )
        progress_percentage = reading_service.get_progress_percentage(
            db, current_user.id, book_uuid
        )
        
        progress_dict = {
            "id": progress.id,
            "user_id": progress.user_id,
            "book_id": progress.book_id,
            "current_page": progress.current_page,
            "updated_at": progress.updated_at,
            "progress_percentage": progress_percentage
        }
        return ReadingProgressResponse.model_validate(progress_dict)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/progress/{book_id}", response_model=ReadingProgressResponse)
async def get_progress(
    book_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reading progress for book"""
    from uuid import UUID
    
    try:
        book_uuid = UUID(book_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID")
    
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    progress = reading_service.get_progress(db, current_user.id, book_uuid)
    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress not found")
    
    progress_percentage = reading_service.get_progress_percentage(
        db, current_user.id, book_uuid
    )
    
    progress_dict = {
        "id": progress.id,
        "user_id": progress.user_id,
        "book_id": progress.book_id,
        "current_page": progress.current_page,
        "updated_at": progress.updated_at,
        "progress_percentage": progress_percentage
    }
    return ReadingProgressResponse.model_validate(progress_dict)


@router.get("/habit", response_model=ReadingHabitResponse)
async def get_habit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reading habit"""
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    habit = reading_service.get_or_create_habit(db, current_user.id)
    return ReadingHabitResponse.model_validate(habit)


@router.put("/habit", response_model=ReadingHabitResponse)
async def update_habit(
    habit_data: ReadingHabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update reading habit goal"""
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    habit = reading_service.update_habit_goal(
        db, current_user.id, habit_data.daily_goal_pages
    )
    return ReadingHabitResponse.model_validate(habit)


@router.get("/stats", response_model=ReadingStatsResponse)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reading statistics"""
    reading_repository = ReadingRepository()
    book_repository = BookRepository()
    reading_service = ReadingService(reading_repository, book_repository)
    
    # Get all progress
    progress_list = reading_service.get_user_progress(db, current_user.id)
    
    # Calculate stats
    total_books_read = len(progress_list)
    total_pages_read = sum(p.current_page for p in progress_list)
    
    # Get habit
    habit = reading_service.get_or_create_habit(db, current_user.id)
    
    return ReadingStatsResponse(
        total_books_read=total_books_read,
        total_pages_read=total_pages_read,
        current_streak=habit.current_streak,
        daily_goal_pages=habit.daily_goal_pages
    )


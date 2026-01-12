from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime, date, timedelta

from app.reading.domain.models import ReadingProgress, ReadingHabit
from app.reading.infrastructure.reading_repository import ReadingRepository
from app.books.domain.models import Book
from app.books.infrastructure.book_repository import BookRepository
from app.infrastructure.messaging import message_broker


class ReadingService:
    def __init__(self, reading_repository: ReadingRepository, book_repository: BookRepository):
        self.reading_repository = reading_repository
        self.book_repository = book_repository

    def update_progress(
        self,
        db: Session,
        user_id: uuid.UUID,
        book_id: uuid.UUID,
        current_page: int
    ) -> ReadingProgress:
        """Update reading progress"""
        # Validate book exists
        book = self.book_repository.get_by_id(db, book_id)
        if not book:
            raise ValueError("Book not found")
        
        # Check if book is in user's library (via UserBook)
        from app.books.infrastructure.user_book_repository import UserBookRepository
        user_book_repo = UserBookRepository()
        user_book = user_book_repo.get_by_user_and_book(db, user_id, book_id)
        
        # Allow progress tracking if:
        # 1. Book is in user's library, OR
        # 2. Book is public and user has access, OR
        # 3. Book is private and user is owner
        if not user_book and not book.is_public and book.owner_id != user_id:
            raise ValueError("Book not in your library")

        # Validate page number
        if current_page < 0 or current_page > book.pages:
            raise ValueError(f"Page number must be between 0 and {book.pages}")

        # Get or create progress
        progress = self.reading_repository.get_progress(db, user_id, book_id)
        if not progress:
            progress = ReadingProgress(
                id=uuid.uuid4(),
                user_id=user_id,
                book_id=book_id,
                current_page=current_page
            )
            progress = self.reading_repository.create_progress(db, progress)
        else:
            progress.current_page = current_page
            progress = self.reading_repository.update_progress(db, progress)

        # Publish event
        message_broker.publish_event(
            "reading_progress_updated",
            {
                "user_id": str(user_id),
                "book_id": str(book_id),
                "pages_read": current_page
            }
        )

        # Check if book finished
        if current_page >= book.pages:
            message_broker.publish_event(
                "book_finished",
                {
                    "user_id": str(user_id),
                    "book_id": str(book_id)
                }
            )

        # Update habit streak
        self._update_habit_streak(db, user_id)

        return progress

    def get_progress(
        self,
        db: Session,
        user_id: uuid.UUID,
        book_id: uuid.UUID
    ) -> Optional[ReadingProgress]:
        """Get reading progress"""
        return self.reading_repository.get_progress(db, user_id, book_id)

    def get_user_progress(self, db: Session, user_id: uuid.UUID) -> List[ReadingProgress]:
        """Get all reading progress for user"""
        return self.reading_repository.get_user_progress(db, user_id)

    def get_progress_percentage(self, db: Session, user_id: uuid.UUID, book_id: uuid.UUID) -> float:
        """Get reading progress percentage"""
        progress = self.reading_repository.get_progress(db, user_id, book_id)
        if not progress:
            return 0.0
        
        book = self.book_repository.get_by_id(db, book_id)
        if not book or book.pages == 0:
            return 0.0
        
        return (progress.current_page / book.pages) * 100

    def get_or_create_habit(self, db: Session, user_id: uuid.UUID) -> ReadingHabit:
        """Get or create reading habit"""
        habit = self.reading_repository.get_habit(db, user_id)
        if not habit:
            habit = ReadingHabit(
                id=uuid.uuid4(),
                user_id=user_id,
                daily_goal_pages=10,
                current_streak=0
            )
            habit = self.reading_repository.create_habit(db, habit)
        return habit

    def update_habit_goal(
        self,
        db: Session,
        user_id: uuid.UUID,
        daily_goal_pages: int
    ) -> ReadingHabit:
        """Update daily reading goal"""
        habit = self.get_or_create_habit(db, user_id)
        habit.daily_goal_pages = daily_goal_pages
        return self.reading_repository.update_habit(db, habit)

    def _update_habit_streak(self, db: Session, user_id: uuid.UUID):
        """Update reading streak based on daily goal"""
        habit = self.get_or_create_habit(db, user_id)
        today = date.today()
        
        # Get pages read today
        today_pages = self.reading_repository.get_pages_read_today(db, user_id)
        
        if today_pages >= habit.daily_goal_pages:
            # Check if last reading was yesterday (continuing streak)
            if habit.last_reading_date:
                last_date = habit.last_reading_date.date()
                if last_date == today:
                    # Already counted today
                    pass
                elif last_date == today - timedelta(days=1):
                    # Continuing streak
                    habit.current_streak += 1
                    habit.last_reading_date = datetime.utcnow()
                else:
                    # Streak broken, reset
                    habit.current_streak = 1
                    habit.last_reading_date = datetime.utcnow()
            else:
                # First time
                habit.current_streak = 1
                habit.last_reading_date = datetime.utcnow()
            
            self.reading_repository.update_habit(db, habit)


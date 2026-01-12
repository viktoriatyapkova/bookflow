from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
import uuid
from datetime import date

from app.reading.domain.models import ReadingProgress, ReadingHabit


class ReadingRepository:
    def create_progress(self, db: Session, progress: ReadingProgress) -> ReadingProgress:
        """Create reading progress"""
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress

    def update_progress(self, db: Session, progress: ReadingProgress) -> ReadingProgress:
        """Update reading progress"""
        db.commit()
        db.refresh(progress)
        return progress

    def get_progress(
        self,
        db: Session,
        user_id: uuid.UUID,
        book_id: uuid.UUID
    ) -> Optional[ReadingProgress]:
        """Get reading progress"""
        return db.query(ReadingProgress).filter(
            and_(
                ReadingProgress.user_id == user_id,
                ReadingProgress.book_id == book_id
            )
        ).first()

    def get_user_progress(self, db: Session, user_id: uuid.UUID) -> List[ReadingProgress]:
        """Get all reading progress for user"""
        return db.query(ReadingProgress).filter(
            ReadingProgress.user_id == user_id
        ).all()

    def get_pages_read_today(self, db: Session, user_id: uuid.UUID) -> int:
        """Get total pages read today by user"""
        today = date.today()
        result = db.query(
            func.sum(ReadingProgress.current_page)
        ).filter(
            and_(
                ReadingProgress.user_id == user_id,
                func.date(ReadingProgress.updated_at) == today
            )
        ).scalar()
        return result or 0

    def create_habit(self, db: Session, habit: ReadingHabit) -> ReadingHabit:
        """Create reading habit"""
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    def update_habit(self, db: Session, habit: ReadingHabit) -> ReadingHabit:
        """Update reading habit"""
        db.commit()
        db.refresh(habit)
        return habit

    def get_habit(self, db: Session, user_id: uuid.UUID) -> Optional[ReadingHabit]:
        """Get reading habit"""
        return db.query(ReadingHabit).filter(
            ReadingHabit.user_id == user_id
        ).first()



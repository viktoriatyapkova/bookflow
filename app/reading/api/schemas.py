from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class ReadingProgressUpdate(BaseModel):
    current_page: int


class ReadingProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    current_page: int
    updated_at: datetime
    progress_percentage: float

    class Config:
        from_attributes = True


class ReadingHabitResponse(BaseModel):
    id: UUID
    user_id: UUID
    daily_goal_pages: int
    current_streak: int
    last_reading_date: Optional[datetime]

    class Config:
        from_attributes = True


class ReadingHabitUpdate(BaseModel):
    daily_goal_pages: int


class ReadingStatsResponse(BaseModel):
    total_books_read: int
    total_pages_read: int
    current_streak: int
    daily_goal_pages: int



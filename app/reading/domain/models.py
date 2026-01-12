from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.infrastructure.database import Base
from app.infrastructure.types import GUID


class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    book_id = Column(GUID(), ForeignKey("books.id"), nullable=False)
    current_page = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    book = relationship("Book", foreign_keys=[book_id])


class ReadingHabit(Base):
    __tablename__ = "reading_habits"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), unique=True, nullable=False)
    daily_goal_pages = Column(Integer, default=10, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    last_reading_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])



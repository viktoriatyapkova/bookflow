from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.users.domain.models import User


class UserRepository:
    def create(self, db: Session, user: User) -> User:
        """Create user"""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_id(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()



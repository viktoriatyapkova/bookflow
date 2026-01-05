from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.users.domain.models import User
from app.users.infrastructure.user_repository import UserRepository
from app.users.application.auth_service import AuthService


class UserService:
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    def create_user(self, db: Session, email: str, password: str) -> User:
        """Create new user"""
        # Check if user exists
        existing_user = self.user_repository.get_by_email(db, email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        hashed_password = self.auth_service.get_password_hash(password)

        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_password
        )
        return self.user_repository.create(db, user)

    def get_user_by_id(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return self.user_repository.get_by_id(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return self.user_repository.get_by_email(db, email)



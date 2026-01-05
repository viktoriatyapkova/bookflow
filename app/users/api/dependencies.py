from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid
from typing import Optional

from app.infrastructure.database import get_db
from app.users.application.auth_service import AuthService
from app.users.infrastructure.user_repository import UserRepository
from app.users.domain.models import User

security = HTTPBearer(auto_error=False)


def get_auth_service() -> AuthService:
    """Dependency for AuthService"""
    user_repository = UserRepository()
    return AuthService(user_repository)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials
    user_id_str = auth_service.get_current_user_id(token)
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user_repository = UserRepository()
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


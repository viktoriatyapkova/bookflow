from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import bcrypt
from sqlalchemy.orm import Session

from app.infrastructure.config import settings
from app.users.domain.models import User
from app.users.infrastructure.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        # Pre-hash long passwords to avoid bcrypt 72-byte limitation
        password_bytes = self._prepare_password(plain_password)
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        # Pre-hash long passwords to avoid bcrypt 72-byte limitation
        password_bytes = self._prepare_password(password)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def _prepare_password(self, password: str) -> bytes:
        """
        Prepare password for bcrypt hashing.
        If password is longer than 72 bytes, pre-hash it with SHA256
        to avoid bcrypt limitation while maintaining security.
        """
        password_bytes = password.encode('utf-8')
        # Bcrypt has 72-byte limit
        if len(password_bytes) > 72:
            # Pre-hash with SHA256 to maintain security while fitting in bcrypt limit
            password_bytes = hashlib.sha256(password_bytes).digest()
        return password_bytes

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = self.user_repository.get_by_email(db, email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_current_user_id(self, token: str) -> Optional[str]:
        """Get user ID from JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            return user_id
        except JWTError:
            return None


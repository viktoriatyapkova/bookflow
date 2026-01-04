from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database import engine, Base
from app.api.v1 import router as api_router
from app.infrastructure.config import settings

# Import all models to register them with Base
from app.users.domain.models import User  # noqa
from app.books.domain.models import Book, UserBook  # noqa
from app.reading.domain.models import ReadingProgress, ReadingHabit  # noqa

# Create database tables (migrations are preferred, but this is a fallback)
# Only create tables if not in test environment and engine is available
import os
if os.getenv("PYTEST_CURRENT_TEST") is None and engine is not None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # Silently fail if database is not available
        pass

app = FastAPI(
    title="BookFlow API",
    description="Серверное приложение для управления личной библиотекой и онлайн-чтения книг",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {"message": "BookFlow API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


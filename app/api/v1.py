from fastapi import APIRouter

from app.users.api.routes import router as users_router
from app.books.api.routes import router as books_router
from app.books.api.library_routes import router as library_router
from app.reading.api.routes import router as reading_router
from app.integrations.api.routes import router as integrations_router

router = APIRouter()

router.include_router(users_router)
router.include_router(books_router)
router.include_router(library_router)
router.include_router(reading_router)
router.include_router(integrations_router)


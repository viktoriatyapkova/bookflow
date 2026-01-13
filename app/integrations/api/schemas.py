from pydantic import BaseModel
from typing import Optional


class BookSearchResult(BaseModel):
    title: str
    author: str
    pages: int
    description: Optional[str] = None
    published_date: Optional[str] = None
    isbn: Optional[str] = None
    thumbnail: Optional[str] = None


class BookSearchResponse(BaseModel):
    books: list[BookSearchResult]
    total: int



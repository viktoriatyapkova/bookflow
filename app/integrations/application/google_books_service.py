import httpx
from typing import List, Optional, Dict, Any
from app.infrastructure.config import settings


class GoogleBooksService:
    def __init__(self):
        self.api_url = settings.GOOGLE_BOOKS_API_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def search_books(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search books using Google Books API"""
        try:
            params = {
                "q": query,
                "maxResults": max_results
            }
            response = await self.client.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            books = []
            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})
                book_data = {
                    "title": volume_info.get("title", "Unknown"),
                    "author": ", ".join(volume_info.get("authors", ["Unknown"])),
                    "pages": volume_info.get("pageCount", 0),
                    "description": volume_info.get("description", ""),
                    "published_date": volume_info.get("publishedDate", ""),
                    "isbn": self._extract_isbn(volume_info.get("industryIdentifiers", [])),
                    "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail", ""),
                }
                books.append(book_data)
            
            return books
        except httpx.HTTPError as e:
            print(f"Error calling Google Books API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def _extract_isbn(self, identifiers: List[Dict[str, str]]) -> Optional[str]:
        """Extract ISBN from identifiers"""
        for identifier in identifiers:
            if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                return identifier.get("identifier")
        return None

    async def get_book_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Get book by ISBN"""
        try:
            params = {
                "q": f"isbn:{isbn}",
                "maxResults": 1
            }
            response = await self.client.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                return None
            
            volume_info = items[0].get("volumeInfo", {})
            return {
                "title": volume_info.get("title", "Unknown"),
                "author": ", ".join(volume_info.get("authors", ["Unknown"])),
                "pages": volume_info.get("pageCount", 0),
                "description": volume_info.get("description", ""),
                "published_date": volume_info.get("publishedDate", ""),
                "isbn": isbn,
                "thumbnail": volume_info.get("imageLinks", {}).get("thumbnail", ""),
            }
        except httpx.HTTPError:
            return None
        except Exception:
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()



import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from ..models import Movie


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

# Watch provider IDs
NETFLIX_PROVIDER_ID = 8


class TMDBService:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.client = httpx.AsyncClient(base_url=TMDB_BASE_URL, timeout=30.0)

    def is_configured(self) -> bool:
        return self.api_key is not None

    async def discover_movies(
        self,
        region: str = "US",
        provider_id: int = NETFLIX_PROVIDER_ID,
        page: int = 1,
        min_rating: float = 6.0,
    ) -> list[dict]:
        """Discover movies available on a specific streaming provider."""
        params = {
            "api_key": self.api_key,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "include_adult": False,
            "include_video": False,
            "page": page,
            "vote_average.gte": min_rating,
            "vote_count.gte": 100,
            "watch_region": region,
            "with_watch_providers": provider_id,
        }

        response = await self.client.get("/discover/movie", params=params)
        response.raise_for_status()
        data = response.json()

        return data.get("results", [])

    async def get_movie_details(self, tmdb_id: int) -> dict:
        """Get full movie details including videos (trailers)."""
        params = {
            "api_key": self.api_key,
            "language": "en-US",
            "append_to_response": "videos",
        }

        response = await self.client.get(f"/movie/{tmdb_id}", params=params)
        response.raise_for_status()
        return response.json()

    async def get_movie_images(self, tmdb_id: int) -> dict:
        """Get movie posters and backdrops."""
        params = {"api_key": self.api_key}

        response = await self.client.get(f"/movie/{tmdb_id}/images", params=params)
        response.raise_for_status()
        return response.json()

    def get_poster_url(self, poster_path: str, size: str = "w342") -> str:
        """Get full poster URL."""
        return f"{TMDB_IMAGE_BASE_URL}/{size}{poster_path}"

    def get_backdrop_url(self, backdrop_path: str, size: str = "w780") -> str:
        """Get full backdrop URL."""
        return f"{TMDB_IMAGE_BASE_URL}/{size}{backdrop_path}"

    def extract_trailer_key(self, videos: dict) -> Optional[str]:
        """Extract YouTube trailer key from videos response."""
        if not videos or "results" not in videos:
            return None

        # Look for official trailers first, then any trailer
        for video in videos["results"]:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                if "official" in video.get("name", "").lower():
                    return video["key"]

        # Fallback to first trailer
        for video in videos["results"]:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return video["key"]

        return None

    async def fetch_and_cache_movies(
        self, db: Session, region: str = "US", count: int = 50
    ) -> list[Movie]:
        """Fetch movies from TMDB and cache in database."""
        movies = []
        page = 1

        while len(movies) < count:
            results = await self.discover_movies(region=region, page=page)

            if not results:
                break

            for movie_data in results:
                if len(movies) >= count:
                    break

                # Check if already cached
                existing = db.query(Movie).filter(Movie.tmdb_id == movie_data["id"]).first()

                if existing:
                    # Update cache if older than 24 hours
                    if existing.updated_at:
                        cache_age = utc_now() - existing.updated_at
                        if cache_age > timedelta(hours=24):
                            await self._update_movie_from_tmdb(db, existing, movie_data)
                    movies.append(existing)
                    continue

                # Fetch full details
                try:
                    details = await self.get_movie_details(movie_data["id"])
                except httpx.HTTPError:
                    continue

                # Create new movie
                movie = self._create_movie_from_tmdb_data(details)
                db.add(movie)
                db.commit()
                db.refresh(movie)
                movies.append(movie)

            page += 1
            if page > 5:  # Limit to 5 pages to avoid rate limits
                break

        return movies

    def _create_movie_from_tmdb_data(self, data: dict) -> Movie:
        """Create Movie model from TMDB API data."""
        videos = data.get("videos", {})
        trailer_key = self.extract_trailer_key(videos)

        # Extract genre names
        genres = [g["name"] for g in data.get("genres", [])]
        genre_str = ", ".join(genres[:3]) if genres else None

        # Parse year from release_date
        year = None
        if data.get("release_date"):
            try:
                year = int(data["release_date"][:4])
            except (ValueError, IndexError):
                pass

        poster_path = data.get("poster_path")
        backdrop_path = data.get("backdrop_path")
        poster_url = self.get_poster_url(poster_path) if poster_path else None
        backdrop_url = self.get_backdrop_url(backdrop_path) if backdrop_path else None

        return Movie(
            tmdb_id=data["id"],
            title=data["title"],
            year=year,
            genre=genre_str,
            poster_url=poster_url,
            backdrop_url=backdrop_url,
            description=data.get("overview"),
            rating=data.get("vote_average"),
            trailer_url=f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else None,
            updated_at=utc_now(),
        )

    async def _update_movie_from_tmdb(self, db: Session, movie: Movie, basic_data: dict):
        """Update cached movie with fresh TMDB data."""
        try:
            tmdb_id: int = movie.tmdb_id  # type: ignore[assignment]
            details = await self.get_movie_details(tmdb_id)
            updated = self._create_movie_from_tmdb_data(details)

            movie.title = updated.title
            movie.year = updated.year
            movie.genre = updated.genre
            movie.poster_url = updated.poster_url
            movie.backdrop_url = updated.backdrop_url
            movie.description = updated.description
            movie.rating = updated.rating
            movie.trailer_url = updated.trailer_url
            movie.updated_at = utc_now()

            db.commit()
        except httpx.HTTPError:
            pass  # Keep existing data if update fails

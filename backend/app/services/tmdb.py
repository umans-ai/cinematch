"""TMDB API client with SQLite caching."""

import json
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from ..models import TMDBCache

TMDB_BASE_URL = "https://api.themoviedb.org/3"
CACHE_TTL = timedelta(hours=24)


class TMDBClient:
    """Pure HTTP client for the TMDB API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get(self, path: str, params: dict | None = None) -> dict:
        all_params = {"api_key": self.api_key, **(params or {})}
        response = httpx.get(f"{TMDB_BASE_URL}{path}", params=all_params)
        response.raise_for_status()
        return response.json()

    def discover_movies(self, region: str = "US", provider: int = 8, page: int = 1) -> list[dict]:
        return self._get(
            "/discover/movie",
            {
                "with_watch_providers": provider,
                "watch_region": region,
                "page": page,
                "sort_by": "popularity.desc",
            },
        ).get("results", [])

    def get_movie_details(self, tmdb_id: int) -> dict:
        return self._get(f"/movie/{tmdb_id}", {"append_to_response": "videos"})

    def get_movie_images(self, tmdb_id: int) -> dict:
        return self._get(f"/movie/{tmdb_id}/images")


class CachedTMDBClient:
    """TMDB client that caches responses in SQLite for 24h."""

    def __init__(self, api_key: str, db: Session):
        self.client = TMDBClient(api_key)
        self.db = db

    def _get_cached(self, key: str) -> list | dict | None:
        entry = self.db.query(TMDBCache).filter(TMDBCache.key == key).first()
        if entry is None:
            return None
        age = datetime.now(timezone.utc) - entry.cached_at.replace(tzinfo=timezone.utc)
        if age > CACHE_TTL:
            self.db.delete(entry)
            self.db.commit()
            return None
        return json.loads(str(entry.data))

    def _set_cached(self, key: str, data: list | dict) -> None:
        entry = TMDBCache(
            key=key,
            data=json.dumps(data),
            cached_at=datetime.now(timezone.utc),
        )
        self.db.merge(entry)
        self.db.commit()

    def discover_movies(self, region: str = "US", provider: int = 8, page: int = 1) -> list[dict]:
        key = f"discover:{region}:{provider}:{page}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        result = self.client.discover_movies(region, provider, page)
        self._set_cached(key, result)
        return result

    def get_movie_details(self, tmdb_id: int) -> dict:
        key = f"details:{tmdb_id}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        result = self.client.get_movie_details(tmdb_id)
        self._set_cached(key, result)
        return result

    def get_movie_images(self, tmdb_id: int) -> dict:
        key = f"images:{tmdb_id}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        result = self.client.get_movie_images(tmdb_id)
        self._set_cached(key, result)
        return result

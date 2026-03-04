"""TMDB API client with caching."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from ..database import Base

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

# Cache TTL: 24 hours
CACHE_TTL_HOURS = 24


class TMDBCache(Base):
    """Cache for TMDB API responses."""

    __tablename__ = "tmdb_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)


def get_cache(db: Session, cache_key: str) -> dict[str, Any] | None:
    """Get cached TMDB response if not expired."""
    cache_entry = db.query(TMDBCache).filter(TMDBCache.cache_key == cache_key).first()
    now = datetime.now(timezone.utc)
    # Handle both timezone-aware and naive datetimes
    if cache_entry:
        expires_at = cache_entry.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at > now:
            return cache_entry.data  # type: ignore[return-value]
    # Clean up expired entry
    if cache_entry:
        db.delete(cache_entry)
        db.commit()
    return None


def set_cache(db: Session, cache_key: str, data: dict) -> None:
    """Cache TMDB response with TTL."""
    # Delete existing entry if any
    existing = db.query(TMDBCache).filter(TMDBCache.cache_key == cache_key).first()
    if existing:
        db.delete(existing)
        db.commit()

    # Create new entry
    cache_entry = TMDBCache(
        cache_key=cache_key,
        data=data,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=CACHE_TTL_HOURS),
    )
    db.add(cache_entry)
    db.commit()


def _make_request(endpoint: str, params: dict | None = None) -> dict:
    """Make authenticated request to TMDB API."""
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY environment variable is not set")

    url = f"{TMDB_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json",
    }

    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params or {}, timeout=30.0)
        response.raise_for_status()
        return response.json()


def discover_movies(
    db: Session,
    region: str = "US",
    provider_id: int | None = None,
    page: int = 1,
) -> dict:
    """Discover movies with optional region and provider filters."""
    cache_key = f"discover:{region}:{provider_id}:{page}"

    # Check cache first
    cached = get_cache(db, cache_key)
    if cached:
        return cached

    # Build params
    params: dict[str, Any] = {
        "region": region,
        "page": page,
        "sort_by": "popularity.desc",
        "include_adult": False,
        "include_video": False,
    }

    if provider_id:
        params["with_watch_providers"] = provider_id
        params["watch_region"] = region

    data = _make_request("/discover/movie", params)

    # Cache the response
    set_cache(db, cache_key, data)

    return data


def get_movie_details(db: Session, tmdb_id: int) -> dict:
    """Get full movie details including videos (trailers)."""
    cache_key = f"movie:{tmdb_id}:details"

    # Check cache first
    cached = get_cache(db, cache_key)
    if cached:
        return cached

    data = _make_request(f"/movie/{tmdb_id}", {"append_to_response": "videos,credits"})

    # Cache the response
    set_cache(db, cache_key, data)

    return data


def get_movie_images(db: Session, tmdb_id: int) -> dict:
    """Get movie posters and backdrops."""
    cache_key = f"movie:{tmdb_id}:images"

    # Check cache first
    cached = get_cache(db, cache_key)
    if cached:
        return cached

    data = _make_request(f"/movie/{tmdb_id}/images")

    # Cache the response
    set_cache(db, cache_key, data)

    return data


def get_image_url(path: str | None, size: str = "w342") -> str | None:
    """Build full TMDB image URL from path."""
    if not path:
        return None
    return f"{TMDB_IMAGE_BASE_URL}/{size}{path}"


def get_trailer_key(videos: dict) -> str | None:
    """Extract YouTube trailer key from videos response."""
    if not videos or "results" not in videos:
        return None

    for video in videos["results"]:
        if video.get("type") == "Trailer" and video.get("site") == "YouTube":
            return video.get("key")

    # Fallback: return first video if no trailer found
    if videos["results"]:
        return videos["results"][0].get("key")

    return None

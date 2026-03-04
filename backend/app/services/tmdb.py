import os
from datetime import datetime, timezone

import httpx

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w342"
BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w780"


def is_configured() -> bool:
    return bool(TMDB_API_KEY)


def poster_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"{POSTER_BASE_URL}{path}"


def backdrop_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"{BACKDROP_BASE_URL}{path}"


def _extract_trailer_key(videos: dict) -> str | None:
    results = videos.get("results", [])
    for video in results:
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            return video.get("key")
    return None


def _extract_genres(genre_list: list[dict]) -> str | None:
    if not genre_list:
        return None
    return ", ".join(g["name"] for g in genre_list[:3])


async def discover_movies(page: int = 1) -> list[dict]:
    """Fetch popular movies from TMDB. Returns [] if not configured."""
    if not is_configured():
        return []

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "page": page,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])


async def get_movie_details(tmdb_id: int) -> dict | None:
    """Fetch full movie details including videos. Returns None if not configured."""
    if not is_configured():
        return None

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "append_to_response": "videos",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{TMDB_BASE_URL}/movie/{tmdb_id}", params=params)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


async def fetch_movies_for_room(count: int = 40) -> list[dict]:
    """
    Fetch and enrich movies from TMDB, returning dicts ready for DB upsert.
    Returns [] if TMDB is not configured.
    """
    if not is_configured():
        return []

    results = []
    page = 1

    while len(results) < count:
        batch = await discover_movies(page=page)
        if not batch:
            break

        for item in batch:
            tmdb_id = item.get("id")
            if not tmdb_id:
                continue

            details = await get_movie_details(tmdb_id)
            if not details:
                continue

            release_year = None
            release_date = details.get("release_date", "")
            if release_date and len(release_date) >= 4:
                try:
                    release_year = int(release_date[:4])
                except ValueError:
                    pass

            results.append({
                "tmdb_id": tmdb_id,
                "title": details.get("title", ""),
                "year": release_year,
                "genre": _extract_genres(details.get("genres", [])),
                "description": details.get("overview") or None,
                "poster_url": poster_url(details.get("poster_path")),
                "backdrop_url": backdrop_url(details.get("backdrop_path")),
                "imdb_rating": details.get("vote_average"),
                "trailer_key": _extract_trailer_key(details.get("videos", {})),
                "fetched_at": datetime.now(timezone.utc),
            })

            if len(results) >= count:
                break

        page += 1
        if page > 5:
            break

    return results

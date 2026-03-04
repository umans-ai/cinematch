import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from ..models import Movie

TMDB_BASE_URL = "https://api.themoviedb.org/3"
CACHE_TTL = timedelta(hours=24)


def get_tmdb_api_key() -> Optional[str]:
    return os.getenv("TMDB_API_KEY")


class TMDBClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json",
        }

    def discover_movies(self, region: str = "US", page: int = 1) -> list[dict]:
        with httpx.Client() as client:
            resp = client.get(
                f"{TMDB_BASE_URL}/discover/movie",
                headers=self.headers,
                params={
                    "include_adult": "false",
                    "include_video": "false",
                    "language": "en-US",
                    "sort_by": "popularity.desc",
                    "watch_region": region,
                    "page": page,
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json().get("results", [])

    def get_movie_details(self, tmdb_id: int) -> dict:
        with httpx.Client() as client:
            resp = client.get(
                f"{TMDB_BASE_URL}/movie/{tmdb_id}",
                headers=self.headers,
                params={
                    "language": "en-US",
                    "append_to_response": "videos",
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

            # Extract YouTube trailer key
            trailer_key = None
            videos = data.get("videos", {}).get("results", [])
            for video in videos:
                if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                    trailer_key = video["key"]
                    break

            return {
                "tmdb_id": data["id"],
                "title": data.get("title", ""),
                "overview": data.get("overview", ""),
                "poster_path": data.get("poster_path"),
                "backdrop_path": data.get("backdrop_path"),
                "vote_average": data.get("vote_average"),
                "popularity": data.get("popularity"),
                "year": int(data["release_date"][:4]) if data.get("release_date") else None,
                "genre": ", ".join(g["name"] for g in data.get("genres", [])),
                "trailer_key": trailer_key,
            }


def sync_movies_to_db(
    db: Session,
    api_key: str,
    region: str = "US",
    pages: int = 1,
) -> list[Movie]:
    client = TMDBClient(api_key)
    now = datetime.now(timezone.utc)
    synced: list[Movie] = []

    for page in range(1, pages + 1):
        results = client.discover_movies(region=region, page=page)

        for item in results:
            tmdb_id = item["id"]

            existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
            if existing and existing.cached_at:
                if now - existing.cached_at.replace(tzinfo=timezone.utc) < CACHE_TTL:
                    synced.append(existing)
                    continue

            if existing:
                movie = existing
            else:
                movie = Movie()
                db.add(movie)

            movie.tmdb_id = tmdb_id
            movie.title = item.get("title", "")
            movie.year = (
                int(item["release_date"][:4]) if item.get("release_date") else None
            )
            movie.genre = ", ".join(
                str(gid) for gid in item.get("genre_ids", [])
            )
            movie.poster_path = item.get("poster_path")
            movie.backdrop_path = item.get("backdrop_path")
            movie.overview = item.get("overview")
            movie.vote_average = item.get("vote_average")
            movie.popularity = item.get("popularity")
            movie.description = (item.get("overview") or "")[:1000]
            movie.cached_at = now
            synced.append(movie)

    db.commit()
    return synced

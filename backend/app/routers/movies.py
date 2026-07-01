import json
import random
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie, MovieAvailability, Room, Vote
from ..routers.providers import PROVIDERS
from ..schemas import MovieResponse, ProviderInfo
from ..services.tmdb import (
    TMDB_API_KEY,
    discover_movies,
    get_image_url,
    get_movie_details,
    get_trailer_key,
)

router = APIRouter()

# Minimum number of movies to keep in a room's pool
MIN_MOVIES_IN_POOL = 50

# Load static movie list from JSON for fallback when TMDB is not available
_DATA_DIR = Path(__file__).parent.parent / "data"
_MOVIES_FILE = _DATA_DIR / "movies.json"

with open(_MOVIES_FILE) as f:
    STATIC_MOVIES: list[dict] = json.load(f)


def _seed_static_movies(
    db: Session, region: str = "US", provider_ids: list[int] | None = None
) -> None:
    """Seed the database with static movies if empty (fallback when no TMDB)."""
    provider_ids = provider_ids or [8]
    if db.query(Movie).count() == 0:
        # First time - create all movies
        for idx, movie_data in enumerate(STATIC_MOVIES):
            movie = Movie(**movie_data)
            db.add(movie)
            db.commit()
            db.refresh(movie)
            # Assign movie to one primary provider (round-robin) for realistic display
            provider_index = idx % len(provider_ids)
            _record_movie_availability(db, movie, region, provider_ids[provider_index])
            # Also add 1-2 additional random providers for variety (30% chance each)
            import random

            for pid in provider_ids:
                if pid != provider_ids[provider_index] and random.random() < 0.3:
                    _record_movie_availability(db, movie, region, pid)
    else:
        # Movies exist but may not be available for this room's providers.
        # Static movies have no TMDB data, so we assign via round-robin
        # only for movies that have NO availability for any of the room's providers.
        movies = db.query(Movie).all()
        for idx, movie in enumerate(movies):
            has_room_provider = (
                db.query(MovieAvailability)
                .filter(
                    MovieAvailability.movie_id == movie.id,
                    MovieAvailability.region == region,
                    MovieAvailability.provider_id.in_(provider_ids),
                )
                .first()
            )
            if not has_room_provider:
                provider_index = idx % len(provider_ids)
                _record_movie_availability(db, movie, region, provider_ids[provider_index])


def _tmdb_to_movie(db: Session, tmdb_movie: dict) -> Movie:
    """Convert TMDB movie data to our Movie model, saving to DB if new."""
    tmdb_id = tmdb_movie.get("id")
    if tmdb_id is None:
        raise ValueError("TMDB movie missing 'id' field")
    tmdb_id = int(tmdb_id)  # Ensure it's an int

    # Check if we already have this movie
    movie = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
    if movie:
        return movie

    # Extract year from release_date
    year = None
    release_date = tmdb_movie.get("release_date")
    if release_date:
        try:
            year = int(release_date[:4])
        except (ValueError, IndexError):
            pass

    # Build genre string from genre_ids (we'll fetch full details for names)
    genre_ids = tmdb_movie.get("genre_ids", [])
    genre = ", ".join(str(g) for g in genre_ids[:3])  # Placeholder, will enhance later

    # Get full details for better data
    try:
        details = get_movie_details(db, tmdb_id)

        # Get proper genre names
        genres = details.get("genres", [])
        genre = ", ".join(g["name"] for g in genres[:3])

        # Get trailer key
        videos = details.get("videos", {})
        trailer_key = get_trailer_key(videos)

        # Get backdrop
        backdrop_path = details.get("backdrop_path")
        backdrop_url = get_image_url(backdrop_path, "w780") if backdrop_path else None

        # Get rating
        rating = int(details.get("vote_average", 0) * 10)  # Store as integer (e.g., 87 for 8.7)

    except Exception:
        # Fallback to basic data if details fetch fails
        details = tmdb_movie
        backdrop_url = None
        trailer_key = None
        rating = int(tmdb_movie.get("vote_average", 0) * 10)

    # Build poster URL
    poster_path = tmdb_movie.get("poster_path")
    poster_url = get_image_url(poster_path, "w342") if poster_path else None

    # Create and save movie
    movie = Movie(
        tmdb_id=tmdb_id,
        title=tmdb_movie.get("title", "Unknown"),
        year=year,
        genre=genre,
        poster_url=poster_url,
        backdrop_url=backdrop_url,
        description=tmdb_movie.get("overview", ""),
        rating=rating,
        trailer_key=trailer_key,
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)

    return movie


def _extract_available_providers(
    db: Session, tmdb_id: int, region: str, room_provider_ids: list[int]
) -> list[int]:
    """Get the subset of room providers where a movie is actually streaming.

    Uses TMDB's watch/providers data (included in movie details) to determine
    which providers actually offer this movie in the given region. Returns only
    provider IDs that are both in the TMDB flatrate list AND in the room's
    selected providers.
    """
    try:
        details = get_movie_details(db, tmdb_id)
        watch_providers = details.get("watch/providers", {}).get("results", {})
        region_data = watch_providers.get(region, {})
        flatrate = region_data.get("flatrate", [])
        tmdb_provider_ids = {p["provider_id"] for p in flatrate}
        return [pid for pid in room_provider_ids if pid in tmdb_provider_ids]
    except Exception:
        return []


def _extract_watch_link(db: Session, tmdb_id: int, region: str) -> str | None:
    """Get TMDB's region-level "where to watch" link for a movie, if any.

    TMDB's watch/providers response includes a region-level ``link`` (a page listing
    where to watch the movie in that region). Returns None when the region is missing,
    has no link, or the details fetch fails.
    """
    try:
        details = get_movie_details(db, tmdb_id)
        watch_providers = details.get("watch/providers", {}).get("results", {})
        region_data = watch_providers.get(region, {})
        return region_data.get("link")
    except Exception:
        return None


def _record_movie_availability(
    db: Session, movie: Movie, region: str, provider_id: int, link: str | None = None
) -> None:
    """Record that a movie is available for a specific region/provider.

    ``link`` is the TMDB region-level watch link; it is stored on creation and refreshed
    on re-sync when TMDB changes it.
    """
    existing = (
        db.query(MovieAvailability)
        .filter(
            MovieAvailability.movie_id == movie.id,
            MovieAvailability.region == region,
            MovieAvailability.provider_id == provider_id,
        )
        .first()
    )
    if not existing:
        availability = MovieAvailability(
            movie_id=movie.id,
            region=region,
            provider_id=provider_id,
            link=link,
        )
        db.add(availability)
        db.commit()
    elif link is not None and existing.link != link:
        # Re-sync: TMDB re-indexed the region and the watch link changed.
        existing.link = link
        db.commit()


def _get_movie_providers(
    db: Session, movie: Movie, region: str, room_provider_ids: list[int]
) -> list[ProviderInfo]:
    """Get available providers for a movie in a specific region, filtered by room's providers."""
    # Query which providers from the room's list are available for this movie
    available_provider_ids = (
        db.query(MovieAvailability.provider_id)
        .filter(
            MovieAvailability.movie_id == movie.id,
            MovieAvailability.region == region,
            MovieAvailability.provider_id.in_(room_provider_ids),
        )
        .all()
    )

    # Build provider info list
    providers = []
    base_url = "https://image.tmdb.org/t/p/original"
    for (provider_id,) in available_provider_ids:
        # Find provider info from PROVIDERS dict
        for key, data in PROVIDERS.items():
            if data["id"] == provider_id:
                providers.append(
                    ProviderInfo(
                        id=provider_id,
                        name=str(data["name"]),
                        logo_url=f"{base_url}{data['logo_path']}",
                    )
                )
                break

    return providers


def _get_movie_watch_link(
    db: Session, movie: Movie, region: str, room_provider_ids: list[int]
) -> str | None:
    """Get the TMDB region-level watch link for a movie, filtered by room providers.

    The link is region-level, so it is identical across a movie's availability rows for a
    given region; we return the first non-null one among the room's selected providers.
    """
    row = (
        db.query(MovieAvailability.link)
        .filter(
            MovieAvailability.movie_id == movie.id,
            MovieAvailability.region == region,
            MovieAvailability.provider_id.in_(room_provider_ids),
            MovieAvailability.link.isnot(None),
        )
        .first()
    )
    return row[0] if row else None


def _movie_to_response(db: Session, movie: Movie, region: str, provider_ids: list[int]) -> dict:
    """Convert a Movie model to a MovieResponse dict with provider info."""
    providers = _get_movie_providers(db, movie, region, provider_ids)

    return {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
        "genre": movie.genre,
        "poster_url": movie.poster_url,
        "backdrop_url": movie.backdrop_url,
        "description": movie.description,
        "rating": movie.rating if movie.rating else None,
        "trailer_key": movie.trailer_key,
        "available_providers": providers,
        "watch_link": _get_movie_watch_link(db, movie, region, provider_ids),
    }


def _ensure_movies_in_pool(db: Session, room: Room, count: int = MIN_MOVIES_IN_POOL) -> None:
    """Ensure room has enough movies in its pool by fetching from TMDB or using static fallback."""
    # Get room's region/provider preferences
    region: str = str(room.region)
    provider_ids: list[int] = room.provider_ids if room.provider_ids else [8]  # type: ignore

    # Get count of movies available for this room's region/providers that haven't been voted on
    voted_movie_ids = db.query(Vote.movie_id).filter(Vote.room_id == room.id).subquery()
    available_movie_ids = (
        db.query(MovieAvailability.movie_id)
        .filter(
            MovieAvailability.region == region,
            MovieAvailability.provider_id.in_(provider_ids),
        )
        .subquery()
    )
    existing_count = (
        db.query(Movie)
        .filter(Movie.id.in_(available_movie_ids))
        .filter(~Movie.id.in_(voted_movie_ids))
        .count()
    )

    if existing_count >= count:
        return

    # If TMDB API key is not available, use static movies as fallback
    if not TMDB_API_KEY:
        _seed_static_movies(db, region, provider_ids)
        return

    # Need to fetch more movies
    needed = count - existing_count
    pages_needed = (needed // 20) + 1  # TMDB returns 20 per page

    fetched_count = 0
    for page in range(1, pages_needed + 1):
        try:
            tmdb_data = discover_movies(db, region=region, provider_ids=provider_ids, page=page)
            results = tmdb_data.get("results", [])

            for tmdb_movie in results:
                # Check if movie already exists
                existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_movie["id"]).first()
                if existing:
                    # Record only the providers this movie is actually on
                    actual_providers = _extract_available_providers(
                        db, int(tmdb_movie["id"]), region, provider_ids
                    )
                    watch_link = _extract_watch_link(db, int(tmdb_movie["id"]), region)
                    for provider_id in actual_providers or [provider_ids[0]]:
                        _record_movie_availability(db, existing, region, provider_id, watch_link)
                else:
                    # Create new movie and record only actual providers
                    movie = _tmdb_to_movie(db, tmdb_movie)
                    actual_providers = _extract_available_providers(
                        db, int(tmdb_movie["id"]), region, provider_ids
                    )
                    watch_link = _extract_watch_link(db, int(tmdb_movie["id"]), region)
                    for provider_id in actual_providers or [provider_ids[0]]:
                        _record_movie_availability(db, movie, region, provider_id, watch_link)
                    fetched_count += 1

                if fetched_count >= needed:
                    break

        except Exception as e:
            # Log error but continue - we might have partial results
            print(f"Error fetching from TMDB page {page}: {e}")
            continue


class RoomInfo(BaseModel):
    code: str
    region: str
    provider_ids: List[int]


class MoviesWithRoomResponse(BaseModel):
    movies: List[MovieResponse]
    room: RoomInfo


@router.get("", response_model=MoviesWithRoomResponse)
def get_movies(
    code: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    refresh: bool = Query(False, description="Force fetch new movies from TMDB"),
    db: Session = Depends(get_db),
):
    """Get movies for a room, fetching from TMDB if needed."""
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Get room's region/providers for filtering
    region: str = str(room.region)
    provider_ids: list[int] = room.provider_ids if room.provider_ids else [8]  # type: ignore

    # If refresh requested, fetch additional movies beyond current pool
    if refresh:
        # Count existing unvoted movies available for this room to determine which page to fetch
        voted_movie_ids = db.query(Vote.movie_id).filter(Vote.room_id == room.id).subquery()
        available_movie_ids = (
            db.query(MovieAvailability.movie_id)
            .filter(
                MovieAvailability.region == region,
                MovieAvailability.provider_id.in_(provider_ids),
            )
            .subquery()
        )
        existing_count = (
            db.query(Movie)
            .filter(Movie.id.in_(available_movie_ids))
            .filter(~Movie.id.in_(voted_movie_ids))
            .count()
        )
        # Fetch additional movies (next batch)
        _ensure_movies_in_pool(db, room, count=existing_count + MIN_MOVIES_IN_POOL)

    # Ensure we have movies in the pool
    _ensure_movies_in_pool(db, room)

    # Get movies available for this room's region/providers that haven't been voted on yet
    voted_movie_ids = db.query(Vote.movie_id).filter(Vote.room_id == room.id).subquery()
    available_movie_ids = (
        db.query(MovieAvailability.movie_id)
        .filter(
            MovieAvailability.region == region,
            MovieAvailability.provider_id.in_(provider_ids),
        )
        .subquery()
    )

    movies = (
        db.query(Movie)
        .filter(Movie.id.in_(available_movie_ids))
        .filter(~Movie.id.in_(voted_movie_ids))
        .order_by(Movie.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    # Build response with provider info for each movie
    movie_responses = [_movie_to_response(db, m, region, provider_ids) for m in movies]

    # Shuffle movies to mix providers (avoid sequential provider grouping)
    random.shuffle(movie_responses)

    return MoviesWithRoomResponse(
        movies=[MovieResponse(**m) for m in movie_responses],
        room=RoomInfo(
            code=str(room.code),
            region=str(room.region),
            provider_ids=provider_ids,
        ),
    )


@router.get("/unvoted", response_model=List[MovieResponse])
def get_unvoted_movies(
    code: str,
    participant_id: int,
    db: Session = Depends(get_db),
):
    """Get movies a specific participant hasn't voted on."""
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Ensure we have movies
    _ensure_movies_in_pool(db, room)

    # Get room's region/providers for filtering
    region: str = str(room.region)
    provider_ids: list[int] = room.provider_ids if room.provider_ids else [8]  # type: ignore

    # Get movies this participant hasn't voted on yet, filtered by availability
    voted_movie_ids = [
        vote.movie_id for vote in db.query(Vote).filter(Vote.participant_id == participant_id).all()
    ]
    available_movie_ids = (
        db.query(MovieAvailability.movie_id)
        .filter(
            MovieAvailability.region == region,
            MovieAvailability.provider_id.in_(provider_ids),
        )
        .subquery()
    )

    movies = (
        db.query(Movie)
        .filter(Movie.id.in_(available_movie_ids))
        .filter(~Movie.id.in_(voted_movie_ids))
        .all()
    )

    # Build response with provider info for each movie
    movie_responses = [_movie_to_response(db, m, region, provider_ids) for m in movies]
    return [MovieResponse(**m) for m in movie_responses]


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie_detail(
    movie_id: int,
    code: str | None = Query(None, description="Room code for provider context"),
    db: Session = Depends(get_db),
):
    """Get detailed info for a single movie."""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Refresh from TMDB if we have a tmdb_id
    if movie.tmdb_id:
        try:
            details = get_movie_details(db, int(movie.tmdb_id))  # type: ignore[arg-type]

            # Update fields if needed
            if not movie.trailer_key:
                videos = details.get("videos", {})
                movie.trailer_key = get_trailer_key(videos)

            if not movie.backdrop_url and details.get("backdrop_path"):
                movie.backdrop_url = get_image_url(details["backdrop_path"], "w780")

            db.commit()
        except Exception:
            # Ignore errors, return cached data
            pass

    # Determine region and provider_ids for provider lookup
    region = "US"
    provider_ids: list[int] = []

    if code:
        room = db.query(Room).filter(Room.code == code).first()
        if room:
            region = str(room.region)
            provider_ids = room.provider_ids if room.provider_ids else []  # type: ignore
    else:
        # No room context - get all available providers for this movie
        all_avail = db.query(MovieAvailability).filter(MovieAvailability.movie_id == movie.id).all()
        # Use region from first availability record
        if all_avail:
            region = str(all_avail[0].region)
            provider_ids = list({int(a.provider_id) for a in all_avail})  # type: ignore

    # If still no provider_ids, use defaults
    if not provider_ids:
        provider_ids = [8]  # Default to Netflix

    # Build response with provider info
    response_data = _movie_to_response(db, movie, str(region), provider_ids)
    return MovieResponse(**response_data)

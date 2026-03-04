import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie, Room, Vote
from ..schemas import MovieResponse
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


def _seed_static_movies(db: Session) -> None:
    """Seed the database with static movies if empty (fallback when no TMDB)."""
    if db.query(Movie).count() == 0:
        for movie_data in STATIC_MOVIES:
            movie = Movie(**movie_data)
            db.add(movie)
        db.commit()


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


def _ensure_movies_in_pool(db: Session, room: Room, count: int = MIN_MOVIES_IN_POOL) -> None:
    """Ensure room has enough movies in its pool by fetching from TMDB or using static fallback."""
    # Get count of existing movies not yet voted by any participant in this room
    voted_movie_ids = db.query(Vote.movie_id).filter(Vote.room_id == room.id).subquery()
    existing_count = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).count()

    if existing_count >= count:
        return

    # If TMDB API key is not available, use static movies as fallback
    if not TMDB_API_KEY:
        _seed_static_movies(db)
        return

    # Need to fetch more movies
    needed = count - existing_count
    pages_needed = (needed // 20) + 1  # TMDB returns 20 per page

    # Get room's region/provider preferences (default to US/Netflix for now)
    # TODO: Read from room model once platform selection is implemented
    region = "US"
    provider_id = 8  # Netflix

    fetched_count = 0
    for page in range(1, pages_needed + 1):
        try:
            tmdb_data = discover_movies(db, region=region, provider_id=provider_id, page=page)
            results = tmdb_data.get("results", [])

            for tmdb_movie in results:
                # Skip if already in DB
                existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_movie["id"]).first()
                if existing:
                    continue

                _tmdb_to_movie(db, tmdb_movie)
                fetched_count += 1

                if fetched_count >= needed:
                    break

        except Exception as e:
            # Log error but continue - we might have partial results
            print(f"Error fetching from TMDB page {page}: {e}")
            continue


@router.get("", response_model=List[MovieResponse])
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

    # If refresh requested, fetch additional movies beyond current pool
    if refresh:
        # Count existing unvoted movies to determine which page to fetch
        voted_movie_ids = db.query(Vote.movie_id).filter(Vote.room_id == room.id).subquery()
        existing_count = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).count()
        # Fetch additional movies (next batch)
        _ensure_movies_in_pool(db, room, count=existing_count + MIN_MOVIES_IN_POOL)

    # Ensure we have movies in the pool
    _ensure_movies_in_pool(db, room)

    # Get movies this room's participants haven't voted on yet
    voted_movie_ids = db.query(Vote.movie_id).filter(Vote.room_id == room.id).subquery()

    movies = (
        db.query(Movie)
        .filter(~Movie.id.in_(voted_movie_ids))
        .order_by(Movie.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return movies


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

    # Get movies this participant hasn't voted on yet
    voted_movie_ids = [
        vote.movie_id for vote in db.query(Vote).filter(Vote.participant_id == participant_id).all()
    ]

    movies = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).all()
    return movies


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
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

    return movie

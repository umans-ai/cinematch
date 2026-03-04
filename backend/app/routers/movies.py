import json
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie, Room, Vote
from ..schemas import MovieDetailResponse, MovieResponse
from ..services.tmdb import TMDBClient, get_tmdb_api_key, sync_movies_to_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Load static movie list from JSON
_DATA_DIR = Path(__file__).parent.parent / "data"
_MOVIES_FILE = _DATA_DIR / "movies.json"

with open(_MOVIES_FILE) as f:
    STATIC_MOVIES: list[dict] = json.load(f)


def seed_movies(db: Session):
    """Seed the database with static movies if empty."""
    if db.query(Movie).count() == 0:
        for movie_data in STATIC_MOVIES:
            movie = Movie(**movie_data)
            db.add(movie)
        db.commit()


@router.get("", response_model=List[MovieResponse])
def get_movies(
    code: str,
    region: str = "US",
    page: int = 1,
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    api_key = get_tmdb_api_key()
    if api_key:
        try:
            movies = sync_movies_to_db(db, api_key, region=region, pages=page)
            return movies
        except Exception:
            logger.exception("TMDB sync failed, falling back to static movies")

    # Fallback to static movies
    seed_movies(db)
    movies = db.query(Movie).all()
    return movies


@router.get("/unvoted", response_model=List[MovieResponse])
def get_unvoted_movies(
    code: str,
    participant_id: int,
    page: int = 1,
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    api_key = get_tmdb_api_key()
    if api_key:
        try:
            sync_movies_to_db(db, api_key, region="US", pages=page)
        except Exception:
            logger.exception("TMDB sync failed, falling back to static movies")
            seed_movies(db)
    else:
        seed_movies(db)

    # Get movies this participant hasn't voted on yet
    voted_movie_ids = [
        vote.movie_id
        for vote in db.query(Vote).filter(Vote.participant_id == participant_id).all()
    ]

    movies = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).all() if voted_movie_ids else db.query(Movie).all()
    return movies


@router.get("/{movie_id}", response_model=MovieDetailResponse)
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Lazy-fetch trailer from TMDB if we have a tmdb_id but no trailer yet
    if movie.tmdb_id and not movie.trailer_key:
        api_key = get_tmdb_api_key()
        if api_key:
            try:
                client = TMDBClient(api_key)
                details = client.get_movie_details(movie.tmdb_id)
                movie.trailer_key = details.get("trailer_key")
                if details.get("genre") and not movie.genre:
                    movie.genre = details["genre"]
                if details.get("overview") and not movie.overview:
                    movie.overview = details["overview"]
                db.commit()
            except Exception:
                logger.exception("Failed to fetch TMDB details")

    return movie

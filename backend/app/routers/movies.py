from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie, Room, Vote
from ..schemas import MovieResponse
from ..services import TMDBService
import json
from pathlib import Path

router = APIRouter()

# Load static movie list from JSON for fallback when TMDB is not configured
_DATA_DIR = Path(__file__).parent.parent / "data"
_MOVIES_FILE = _DATA_DIR / "movies.json"

with open(_MOVIES_FILE) as f:
    STATIC_MOVIES: list[dict] = json.load(f)


def seed_static_movies(db: Session):
    """Seed the database with static movies if empty (TMDB fallback)."""
    for movie_data in STATIC_MOVIES:
        movie = Movie(**movie_data)
        db.add(movie)
    db.commit()


async def seed_movies_from_tmdb(db: Session, count: int = 50):
    """Fetch movies from TMDB and cache in database if empty."""
    if db.query(Movie).count() == 0:
        tmdb = TMDBService()
        if tmdb.is_configured():
            await tmdb.fetch_and_cache_movies(db, count=count)
        else:
            # Fallback to static movies if TMDB not configured
            seed_static_movies(db)


@router.get("", response_model=List[MovieResponse])
async def get_movies(code: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Seed movies from TMDB if needed
    await seed_movies_from_tmdb(db)

    movies = db.query(Movie).all()
    return movies


@router.get("/unvoted", response_model=List[MovieResponse])
async def get_unvoted_movies(code: str, participant_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    await seed_movies_from_tmdb(db)

    # Get movies this participant hasn't voted on yet
    voted_movie_ids = [
        vote.movie_id for vote in db.query(Vote).filter(Vote.participant_id == participant_id).all()
    ]

    movies = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).all()
    return movies


@router.post("/refresh")
async def refresh_movies(code: str, db: Session = Depends(get_db)):
    """Fetch a new batch of movies from TMDB."""
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    tmdb = TMDBService()
    # Fetch next page of movies
    existing_count = db.query(Movie).count()
    movies = await tmdb.fetch_and_cache_movies(db, count=50)

    return {"message": f"Added {len(movies)} movies", "total": existing_count + len(movies)}

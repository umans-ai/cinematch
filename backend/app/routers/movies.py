import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie, Room, Vote
from ..schemas import MovieResponse

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
def get_movies(code: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Seed movies if needed
    seed_movies(db)

    movies = db.query(Movie).all()
    return movies


@router.get("/unvoted", response_model=List[MovieResponse])
def get_unvoted_movies(code: str, participant_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    seed_movies(db)

    # Get movies this participant hasn't voted on yet
    voted_movie_ids = [
        vote.movie_id for vote in db.query(Vote).filter(Vote.participant_id == participant_id).all()
    ]

    movies = db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).all()
    return movies

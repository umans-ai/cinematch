import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import TMDB_API_KEY
from ..database import get_db
from ..models import Movie, Room, Vote
from ..schemas import MovieDetailResponse, MovieResponse
from ..services.tmdb import CachedTMDBClient

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


@router.get("/discover", response_model=List[MovieResponse])
def discover_movies(
    region: str = "US",
    provider: int = 8,
    page: int = 1,
    db: Session = Depends(get_db),
):
    if not TMDB_API_KEY:
        raise HTTPException(status_code=503, detail="TMDB_API_KEY not configured")

    client = CachedTMDBClient(api_key=TMDB_API_KEY, db=db)
    tmdb_movies = client.discover_movies(region=region, provider=provider, page=page)

    results = []
    for m in tmdb_movies:
        tmdb_id = m["id"]
        movie = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
        if not movie:
            release_year = int(m["release_date"][:4]) if m.get("release_date") else None
            movie = Movie(
                title=m["title"],
                year=release_year,
                description=m.get("overview", ""),
                poster_path=m.get("poster_path"),
                backdrop_path=m.get("backdrop_path"),
                imdb_rating=m.get("vote_average"),
                tmdb_id=tmdb_id,
            )
            db.add(movie)
            db.commit()
            db.refresh(movie)
        results.append(movie)

    return results


@router.get("/{movie_id}", response_model=MovieDetailResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # If this movie came from TMDB and has no trailer yet, fetch details
    if movie.tmdb_id and not movie.trailer_key and TMDB_API_KEY:
        client = CachedTMDBClient(api_key=TMDB_API_KEY, db=db)
        details = client.get_movie_details(movie.tmdb_id)  # ty: ignore[invalid-argument-type]
        videos = details.get("videos", {}).get("results", [])
        trailer = next(
            (v for v in videos if v["site"] == "YouTube" and v["type"] == "Trailer"),
            None,
        )
        if trailer:
            movie.trailer_key = trailer["key"]
            db.commit()
            db.refresh(movie)

    return movie

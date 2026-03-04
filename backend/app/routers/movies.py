import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Movie, Room, Vote
from ..schemas import MovieResponse
from ..services import tmdb

logger = logging.getLogger(__name__)

router = APIRouter()

_DATA_DIR = Path(__file__).parent.parent / "data"
_MOVIES_FILE = _DATA_DIR / "movies.json"

with open(_MOVIES_FILE) as f:
    STATIC_MOVIES: list[dict] = json.load(f)

CACHE_TTL = timedelta(hours=24)


def _is_cache_stale(db: Session) -> bool:
    """Returns True if TMDB movies need to be refreshed."""
    newest = (
        db.query(Movie)
        .filter(Movie.fetched_at.isnot(None))
        .order_by(Movie.fetched_at.desc())
        .first()
    )
    if not newest or newest.fetched_at is None:
        return True
    age = datetime.now(timezone.utc) - newest.fetched_at.replace(tzinfo=timezone.utc)
    return age > CACHE_TTL


def seed_static_movies(db: Session) -> None:
    """Seed the database with static movies if empty."""
    if db.query(Movie).count() == 0:
        for movie_data in STATIC_MOVIES:
            db.add(Movie(**movie_data))
        db.commit()


async def _sync_tmdb_movies(db: Session) -> None:
    """Fetch movies from TMDB and upsert into DB."""
    try:
        movies_data = await tmdb.fetch_movies_for_room(count=40)
    except Exception as exc:
        logger.warning("TMDB fetch failed, keeping existing movies: %s", exc)
        return

    if not movies_data:
        return

    for data in movies_data:
        existing = db.query(Movie).filter(Movie.tmdb_id == data["tmdb_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(Movie(**data))

    db.commit()


@router.get("", response_model=List[MovieResponse])
async def get_movies(code: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if tmdb.is_configured():
        if _is_cache_stale(db):
            await _sync_tmdb_movies(db)
    else:
        seed_static_movies(db)

    return db.query(Movie).all()


@router.get("/unvoted", response_model=List[MovieResponse])
async def get_unvoted_movies(code: str, participant_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if tmdb.is_configured():
        if _is_cache_stale(db):
            await _sync_tmdb_movies(db)
    else:
        seed_static_movies(db)

    voted_movie_ids = [
        vote.movie_id
        for vote in db.query(Vote).filter(Vote.participant_id == participant_id).all()
    ]
    return db.query(Movie).filter(~Movie.id.in_(voted_movie_ids)).all()

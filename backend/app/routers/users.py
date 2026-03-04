from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_optional_user_id
from ..database import get_db
from ..models import Movie, Participant, Room, Vote
from ..schemas import MovieResponse

router = APIRouter()


def require_user_id(request: Request) -> str:
    """Require a valid Clerk user ID or raise 401."""
    user_id = get_optional_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


class RoomSummaryResponse(BaseModel):
    code: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/me/history", response_model=List[MovieResponse])
def get_history(request: Request, db: Session = Depends(get_db)):
    """Return movies the authenticated user liked, deduped across all rooms."""
    user_id = require_user_id(request)

    liked_movie_ids: set[int] = set()
    movies: list[Movie] = []

    participants = (
        db.query(Participant).filter(Participant.clerk_user_id == user_id).all()
    )

    for participant in participants:
        votes = (
            db.query(Vote)
            .filter(Vote.participant_id == participant.id, Vote.liked.is_(True))
            .all()
        )
        for vote in votes:
            if vote.movie_id not in liked_movie_ids:
                liked_movie_ids.add(vote.movie_id)
                movie = db.query(Movie).filter(Movie.id == vote.movie_id).first()
                if movie:
                    movies.append(movie)

    return movies


@router.get("/me/rooms", response_model=List[RoomSummaryResponse])
def get_rooms(request: Request, db: Session = Depends(get_db)):
    """Return rooms the authenticated user has joined."""
    user_id = require_user_id(request)

    participants = (
        db.query(Participant).filter(Participant.clerk_user_id == user_id).all()
    )

    seen_room_ids: set[int] = set()
    rooms: list[Room] = []

    for participant in participants:
        if participant.room_id not in seen_room_ids:
            seen_room_ids.add(participant.room_id)
            room = db.query(Room).filter(Room.id == participant.room_id).first()
            if room:
                rooms.append(room)

    return rooms

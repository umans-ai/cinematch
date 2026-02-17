from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Room, Participant, Vote, Movie
from ..schemas import VoteCreate, VoteResponse, MatchResponse

router = APIRouter()


def get_session_id(request: Request) -> str:
    return request.cookies.get("session_id", "")


@router.post("", response_model=VoteResponse)
def create_vote(
    code: str,
    vote: VoteCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    session_id = get_session_id(request)
    participant = db.query(Participant).filter(
        Participant.room_id == room.id,
        Participant.session_id == session_id
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant in this room")

    # Check if already voted on this movie
    existing = db.query(Vote).filter(
        Vote.room_id == room.id,
        Vote.participant_id == participant.id,
        Vote.movie_id == vote.movie_id
    ).first()

    if existing:
        # Update existing vote
        existing.liked = vote.liked
        db.commit()
        db.refresh(existing)
        return existing

    new_vote = Vote(
        room_id=room.id,
        participant_id=participant.id,
        movie_id=vote.movie_id,
        liked=vote.liked
    )
    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)
    return new_vote


@router.get("/matches", response_model=List[MatchResponse])
def get_matches(code: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Find movies where all participants liked
    participants = db.query(Participant).filter(Participant.room_id == room.id).all()
    participant_ids = [p.id for p in participants]

    if len(participant_ids) < 2:
        return []

    # Get all movies voted liked by each participant
    matches = []
    movies = db.query(Movie).all()

    for movie in movies:
        votes = db.query(Vote).filter(
            Vote.room_id == room.id,
            Vote.movie_id == movie.id,
            Vote.liked.is_(True)
        ).all()

        voter_ids = [v.participant_id for v in votes]

        # Check if all participants liked this movie
        if set(participant_ids).issubset(set(voter_ids)):
            matches.append(MatchResponse(
                movie=movie,
                participants=[p.name for p in participants]
            ))

    return matches

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Participant, Room
from ..schemas import ParticipantCreate, ParticipantResponse, RoomResponse

router = APIRouter()


def get_session_id(request: Request) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("", response_model=RoomResponse)
def create_room(db: Session = Depends(get_db)):
    max_attempts = 10
    for _ in range(max_attempts):
        room = Room()
        db.add(room)
        try:
            db.commit()
            db.refresh(room)
            return room
        except IntegrityError:
            db.rollback()
            continue
    raise HTTPException(status_code=500, detail="Could not generate unique room code")


@router.get("/{code}", response_model=RoomResponse)
def get_room(code: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/{code}/join", response_model=ParticipantResponse)
def join_room(
    code: str,
    participant: ParticipantCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.code == code).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    session_id = get_session_id(request)

    # Check if already joined
    existing = (
        db.query(Participant)
        .filter(Participant.room_id == room.id, Participant.session_id == session_id)
        .first()
    )

    if existing:
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return existing

    # Check room capacity (max 2 for now)
    participant_count = db.query(Participant).filter(Participant.room_id == room.id).count()

    if participant_count >= 2:
        raise HTTPException(status_code=400, detail="Room is full")

    # Get user_id from cookie if authenticated
    user_id_str = request.cookies.get("user_id")
    user_id = int(user_id_str) if user_id_str else None

    new_participant = Participant(
        room_id=room.id, name=participant.name, session_id=session_id, user_id=user_id
    )
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return new_participant

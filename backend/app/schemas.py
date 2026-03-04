from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RoomCreate(BaseModel):
    pass


class RoomResponse(BaseModel):
    id: int
    code: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    name: str


class ParticipantResponse(BaseModel):
    id: int
    name: str
    session_id: str

    class Config:
        from_attributes = True


class MovieResponse(BaseModel):
    id: int
    title: str
    year: Optional[int] = None
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None  # TMDB vote_average
    trailer_key: Optional[str] = None  # YouTube trailer key

    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    movie_id: int
    liked: bool


class VoteResponse(BaseModel):
    id: int
    movie_id: int
    participant_id: int
    liked: bool

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    movie: MovieResponse
    participants: List[str]

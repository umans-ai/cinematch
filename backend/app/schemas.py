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
    year: Optional[int]
    genre: Optional[str]
    poster_url: Optional[str]
    description: Optional[str]
    tmdb_id: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    vote_average: Optional[float] = None

    class Config:
        from_attributes = True


class MovieDetailResponse(MovieResponse):
    overview: Optional[str] = None
    trailer_key: Optional[str] = None

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

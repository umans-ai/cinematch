from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


class RoomCreate(BaseModel):
    region: str = "US"
    provider_ids: List[int] = [8]

    @field_validator("provider_ids")
    @classmethod
    def validate_provider_ids(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError("At least one provider must be selected")
        if len(v) > 5:
            raise ValueError("Maximum 5 providers allowed")
        return v


class RoomResponse(BaseModel):
    id: int
    code: str
    created_at: datetime
    is_active: bool
    region: str
    provider_ids: List[int]

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

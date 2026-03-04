import random
import string

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


def generate_room_code():
    return "".join(random.choices(string.digits, k=4))


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(4), unique=True, index=True, default=generate_room_code)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    participants = relationship("Participant", back_populates="room", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="room", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    name = Column(String(50))
    session_id = Column(String(100), unique=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="participants")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    participant_id = Column(Integer, ForeignKey("participants.id"))
    liked = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="votes")
    movie = relationship("Movie", back_populates="votes")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    title = Column(String(200), nullable=False)
    year = Column(Integer)
    genre = Column(String(100))
    poster_url = Column(String(500))
    backdrop_url = Column(String(500))
    description = Column(String(2000))
    rating = Column(Float)  # IMDB rating 0-10
    trailer_url = Column(String(500))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    votes = relationship("Vote", back_populates="movie")

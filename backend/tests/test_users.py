"""Tests for /api/v1/users endpoints."""
import time
from unittest.mock import MagicMock, patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.database import get_db, init_db
from app.main import app
from app.models import Movie, Room, Vote

init_db()

client = TestClient(app)

_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()


def _make_token(sub: str = "user_test123") -> str:
    payload = {
        "sub": sub,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm="RS256")


def _mock_jwks_patches(token: str):
    mock_key = MagicMock()
    mock_key.key = _PUBLIC_KEY
    mock_client = MagicMock()
    mock_client.get_signing_key_from_jwt.return_value = mock_key
    return (
        patch("app.auth.CLERK_JWKS_URL", "https://clerk.example.com/.well-known/jwks.json"),
        patch("app.auth._get_jwks_client", return_value=mock_client),
    )


def _create_room_and_join(clerk_user_id: str | None = None) -> tuple[str, int]:
    """Create a room and join it. Returns (room_code, participant_id)."""
    room_resp = client.post("/api/v1/rooms")
    code = room_resp.json()["code"]

    token = _make_token(sub=clerk_user_id) if clerk_user_id else None
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    if token:
        ctx1, ctx2 = _mock_jwks_patches(token)
        with ctx1, ctx2:
            join_resp = client.post(
                f"/api/v1/rooms/{code}/join",
                json={"name": "TestUser"},
                headers=headers,
            )
    else:
        join_resp = client.post(f"/api/v1/rooms/{code}/join", json={"name": "TestUser"})

    participant_id = join_resp.json()["id"]
    return code, participant_id


class TestHistoryEndpoint:
    def test_unauthenticated_returns_401(self):
        resp = client.get("/api/v1/users/me/history")
        assert resp.status_code == 401

    def test_authenticated_returns_liked_movies(self):
        clerk_id = "user_history_test"
        token = _make_token(sub=clerk_id)
        ctx1, ctx2 = _mock_jwks_patches(token)

        code, participant_id = _create_room_and_join(clerk_user_id=clerk_id)

        # Add a movie and cast a vote via DB directly
        db = next(get_db())
        movie = Movie(title="Test Movie", year=2024, genre="Drama")
        db.add(movie)
        db.commit()
        db.refresh(movie)
        movie_id = movie.id  # capture before session closes

        vote = Vote(
            room_id=db.query(Room).filter(Room.code == code).first().id,
            participant_id=participant_id,
            movie_id=movie_id,
            liked=True,
        )
        db.add(vote)
        db.commit()
        db.close()

        with ctx1, ctx2:
            resp = client.get(
                "/api/v1/users/me/history",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        movie_ids = [m["id"] for m in data]
        assert movie_id in movie_ids

    def test_only_liked_movies_returned(self):
        clerk_id = "user_likes_only"
        token = _make_token(sub=clerk_id)
        ctx1, ctx2 = _mock_jwks_patches(token)

        code, participant_id = _create_room_and_join(clerk_user_id=clerk_id)

        db = next(get_db())
        room = db.query(Room).filter(Room.code == code).first()
        room_id = room.id

        liked_movie = Movie(title="Liked Movie", year=2024, genre="Action")
        disliked_movie = Movie(title="Disliked Movie", year=2024, genre="Horror")
        db.add_all([liked_movie, disliked_movie])
        db.commit()
        db.refresh(liked_movie)
        db.refresh(disliked_movie)
        liked_id = liked_movie.id
        disliked_id = disliked_movie.id

        db.add(Vote(room_id=room_id, participant_id=participant_id, movie_id=liked_id, liked=True))
        db.add(
            Vote(room_id=room_id, participant_id=participant_id, movie_id=disliked_id, liked=False)
        )
        db.commit()
        db.close()

        with ctx1, ctx2:
            resp = client.get(
                "/api/v1/users/me/history",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        returned_ids = [m["id"] for m in data]
        assert liked_id in returned_ids
        assert disliked_id not in returned_ids


class TestRoomsEndpoint:
    def test_unauthenticated_returns_401(self):
        resp = client.get("/api/v1/users/me/rooms")
        assert resp.status_code == 401

    def test_authenticated_returns_user_rooms(self):
        clerk_id = "user_rooms_test"
        token = _make_token(sub=clerk_id)
        ctx1, ctx2 = _mock_jwks_patches(token)

        code, _ = _create_room_and_join(clerk_user_id=clerk_id)

        with ctx1, ctx2:
            resp = client.get(
                "/api/v1/users/me/rooms",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        codes = [r["code"] for r in data]
        assert code in codes

    def test_rooms_have_expected_fields(self):
        clerk_id = "user_rooms_fields"
        token = _make_token(sub=clerk_id)
        ctx1, ctx2 = _mock_jwks_patches(token)

        _create_room_and_join(clerk_user_id=clerk_id)

        with ctx1, ctx2:
            resp = client.get(
                "/api/v1/users/me/rooms",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        for room in resp.json():
            assert "code" in room
            assert "created_at" in room
            assert "is_active" in room

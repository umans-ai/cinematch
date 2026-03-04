"""Tests for room endpoints, including Clerk user ID storage on join."""
import time
from unittest.mock import MagicMock, patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app

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


def _mock_jwks_context(token: str):
    """Context manager that patches JWKS verification to use test key."""
    mock_key = MagicMock()
    mock_key.key = _PUBLIC_KEY
    mock_client = MagicMock()
    mock_client.get_signing_key_from_jwt.return_value = mock_key
    return (
        patch("app.auth.CLERK_JWKS_URL", "https://clerk.example.com/.well-known/jwks.json"),
        patch("app.auth._get_jwks_client", return_value=mock_client),
    )


def _create_room() -> str:
    resp = client.post("/api/v1/rooms")
    assert resp.status_code == 200
    return resp.json()["code"]


class TestJoinWithClerkUserId:
    def test_join_without_auth_stores_null_clerk_user_id(self):
        code = _create_room()
        resp = client.post(f"/api/v1/rooms/{code}/join", json={"name": "Alice"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["clerk_user_id"] is None

    def test_join_with_valid_token_stores_clerk_user_id(self):
        code = _create_room()
        token = _make_token(sub="user_clerk_abc")

        ctx1, ctx2 = _mock_jwks_context(token)
        with ctx1, ctx2:
            resp = client.post(
                f"/api/v1/rooms/{code}/join",
                json={"name": "Bob"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["clerk_user_id"] == "user_clerk_abc"

    def test_join_with_invalid_token_falls_back_to_null(self):
        code = _create_room()
        resp = client.post(
            f"/api/v1/rooms/{code}/join",
            json={"name": "Carol"},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["clerk_user_id"] is None

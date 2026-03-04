"""Tests for JWT authentication via Clerk JWKS."""
import time
from unittest.mock import MagicMock, patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.requests import Request

# Generate a test RSA key pair once for the module
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()


def _make_token(sub: str = "user_test123", exp_offset: int = 3600) -> str:
    """Create a signed JWT using the test private key."""
    payload = {
        "sub": sub,
        "iat": int(time.time()),
        "exp": int(time.time()) + exp_offset,
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm="RS256")


def _make_mock_signing_key(token: str) -> MagicMock:
    """Return a mock signing key wrapping the test public key."""
    mock_key = MagicMock()
    mock_key.key = _PUBLIC_KEY
    return mock_key


def _make_request(token: str | None = None) -> Request:
    """Build a minimal Starlette Request with optional Authorization header."""
    headers: dict[str, str] = {}
    if token is not None:
        headers["authorization"] = f"Bearer {token}"
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
    }
    return Request(scope)


class TestGetOptionalUserId:
    def test_missing_header_returns_none(self):
        from app.auth import get_optional_user_id

        request = _make_request(token=None)
        assert get_optional_user_id(request) is None

    def test_empty_bearer_returns_none(self):
        from app.auth import get_optional_user_id

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"authorization", b"Bearer ")],
        }
        request = Request(scope)
        assert get_optional_user_id(request) is None

    def test_valid_token_returns_sub(self):
        from app.auth import get_optional_user_id

        token = _make_token(sub="user_abc123")
        request = _make_request(token=token)

        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.return_value = _make_mock_signing_key(token)

        with (
            patch("app.auth.CLERK_JWKS_URL", "https://clerk.example.com/.well-known/jwks.json"),
            patch("app.auth._get_jwks_client", return_value=mock_client),
        ):
            result = get_optional_user_id(request)

        assert result == "user_abc123"

    def test_expired_token_returns_none(self):
        from app.auth import get_optional_user_id

        token = _make_token(sub="user_abc123", exp_offset=-3600)  # expired 1 hour ago
        request = _make_request(token=token)

        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.return_value = _make_mock_signing_key(token)

        with (
            patch("app.auth.CLERK_JWKS_URL", "https://clerk.example.com/.well-known/jwks.json"),
            patch("app.auth._get_jwks_client", return_value=mock_client),
        ):
            result = get_optional_user_id(request)

        assert result is None

    def test_invalid_token_returns_none(self):
        from app.auth import get_optional_user_id

        request = _make_request(token="not.a.valid.jwt")

        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.side_effect = jwt.exceptions.InvalidTokenError(
            "bad token"
        )

        with (
            patch("app.auth.CLERK_JWKS_URL", "https://clerk.example.com/.well-known/jwks.json"),
            patch("app.auth._get_jwks_client", return_value=mock_client),
        ):
            result = get_optional_user_id(request)

        assert result is None

    def test_no_jwks_url_returns_none(self):
        from app.auth import get_optional_user_id

        token = _make_token()
        request = _make_request(token=token)

        with patch("app.auth.CLERK_JWKS_URL", ""):
            result = get_optional_user_id(request)

        assert result is None

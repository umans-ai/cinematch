import logging
import os
from functools import lru_cache
from typing import Optional

import jwt
from fastapi import Request

logger = logging.getLogger(__name__)

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "")


@lru_cache(maxsize=1)
def _get_jwks_client() -> jwt.PyJWKClient:
    if not CLERK_JWKS_URL:
        raise ValueError("CLERK_JWKS_URL environment variable not set")
    return jwt.PyJWKClient(CLERK_JWKS_URL, cache_jwk_set=True, lifespan=3600)


def get_optional_user_id(request: Request) -> Optional[str]:
    """Extract Clerk user ID from Authorization header. Returns None if missing/invalid."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    if not token or not CLERK_JWKS_URL:
        return None

    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return payload.get("sub")
    except Exception as e:
        logger.debug("JWT verification failed: %s", e)
        return None

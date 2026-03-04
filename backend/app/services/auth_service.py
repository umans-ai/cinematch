import os
from datetime import datetime, timedelta

from jose import JWTError, jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "15"))


def create_magic_link_token(email: str) -> str:
    """Create JWT token for magic link authentication"""
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {"email": email, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_magic_link_token(token: str) -> str | None:
    """Verify JWT token and return email if valid, None otherwise"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("email")
        return email if email else None
    except JWTError:
        return None


def send_magic_link_email(email: str, token: str):
    """Send magic link email (dev: log to console, prod: use SMTP/SES)"""
    magic_link = f"http://localhost:3000/auth/verify?token={token}"
    print(f"\n{'=' * 60}")
    print(f"MAGIC LINK for {email}")
    print(f"{magic_link}")
    print(f"{'=' * 60}\n")
    # TODO: In production, use SMTP or AWS SES to send actual email

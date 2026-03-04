from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class MagicLinkRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    email: str
    name: str | None

    class Config:
        from_attributes = True


@router.post("/request-magic-link")
def request_magic_link(body: MagicLinkRequest):
    """Request a magic link for email authentication"""
    token = auth_service.create_magic_link_token(body.email)
    auth_service.send_magic_link_email(body.email, token)
    return {"message": "Check your email for the magic link"}


@router.get("/verify")
def verify_magic_link(token: str, response: Response, db: Session = Depends(get_db)):
    """Verify magic link token and authenticate user"""
    email = auth_service.verify_magic_link_token(token)

    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=email.split("@")[0])
        db.add(user)

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Set user_id cookie
    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,
        max_age=30 * 24 * 60 * 60,  # 30 days
        samesite="lax",
    )

    return {"message": "Authentication successful", "user": UserResponse.from_orm(user)}


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie("user_id")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

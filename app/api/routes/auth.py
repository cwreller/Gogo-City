"""Auth endpoints: register, login, Google OAuth, and profile update."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user, hash_password, verify_password
from app.core.config import get_settings
from app.db.session import get_db
from app.models import User
from app.schemas.auth import (
    GoogleLoginRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateMeRequest,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new account and return an access token."""
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(
        email=body.email,
        username=body.username,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id, user.username, user.display_name or "", user.email)
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Exchange email + password for an access token."""
    user = db.query(User).filter(User.email == body.email).first()
    if user and not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google sign-in. Please sign in with Google.",
        )
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(
        access_token=create_access_token(user.id, user.username, user.display_name or "", user.email)
    )


@router.post("/google", response_model=TokenResponse)
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Verify a Google ID token and return an app access token."""
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=501, detail="Google sign-in is not configured")

    try:
        payload = google_id_token.verify_oauth2_token(
            body.id_token,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    gid = payload["sub"]
    email = payload.get("email", "")
    name = payload.get("name", "")

    user = db.query(User).filter(User.google_id == gid).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()

    if user:
        if not user.google_id:
            user.google_id = gid
            db.commit()
            db.refresh(user)
    else:
        user = User(
            email=email,
            username=email,
            display_name=name,
            password_hash=None,
            google_id=gid,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id, user.username, user.display_name or "", user.email)
    )


@router.patch("/me", response_model=TokenResponse)
def update_me(
    body: UpdateMeRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    """Update the current user's profile and return a fresh token."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.display_name is not None:
        user.display_name = body.display_name
    db.commit()
    db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user.id, user.username, user.display_name or "", user.email)
    )

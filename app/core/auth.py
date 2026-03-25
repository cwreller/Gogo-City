"""Auth helpers: password hashing, JWT creation/decoding, and the get_current_user dependency.

This is the single seam for auth. To swap to Supabase Auth (or any other provider) later:
  1. Replace the body of `get_current_user` to verify a Supabase JWT instead.
  2. Remove `hash_password` / `verify_password` (Supabase owns passwords).
  3. Remove `create_access_token` (Supabase issues tokens).
  4. Nothing else in the codebase needs to change.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt as _bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings

_bearer = HTTPBearer()


# ── Password helpers ─────────────────────────────────────────────────
# Use bcrypt directly to avoid passlib/bcrypt version-compatibility issues.

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ── JWT helpers ──────────────────────────────────────────────────────

def _admin_email_list() -> list[str]:
    settings = get_settings()
    return [e.strip().lower() for e in settings.admin_emails.split(",") if e.strip()]


def create_access_token(user_id: UUID, username: str = "", display_name: str = "", email: str = "") -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "username": username,
        "display_name": display_name or username,
        "email": email,
        "is_admin": email.lower() in _admin_email_list() if email else False,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# ── FastAPI dependency ───────────────────────────────────────────────

def _decode_token(credentials: HTTPAuthorizationCredentials) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if not payload.get("sub"):
            raise JWTError("missing sub")
        return payload
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UUID:
    """Decode Bearer token and return the user's UUID.

    Raises HTTP 401 if the token is missing, expired, or invalid.
    To swap auth providers, replace only this function.
    """
    payload = _decode_token(credentials)
    return UUID(payload["sub"])


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UUID:
    """Like get_current_user but raises 403 if the user isn't an admin."""
    payload = _decode_token(credentials)
    email = payload.get("email", "")
    if email.lower() not in _admin_email_list():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return UUID(payload["sub"])

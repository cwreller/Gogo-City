# Catherine - Sprint Tasks

## Status
- [x] Chicago CSV — 43 tasks imported into DB with XP assigned ✅

---

## Up Next

### 1. Backend — `PATCH /api/auth/me` (display name editing)

Add one endpoint to `app/api/routes/auth.py` so users can update their display name.

**Step 1 — Add `UpdateMeRequest` to `app/schemas/auth.py`:**
```python
class UpdateMeRequest(BaseModel):
    display_name: str | None = None
```

**Step 2 — Add the endpoint to `app/api/routes/auth.py`:**
```python
from uuid import UUID
from app.core.auth import get_current_user

@router.patch("/me", response_model=TokenResponse)
def update_me(body: UpdateMeRequest, db: Session = Depends(get_db), user_id: UUID = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.display_name is not None:
        user.display_name = body.display_name
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(user.id, user.username, user.display_name or ""))
```

**Test it** at http://localhost:8000/docs — look for `PATCH /api/auth/me`. Send `{"display_name": "New Name"}` with a Bearer token.

---

## Key Files
- `app/api/routes/auth.py` — add `PATCH /me` here
- `app/schemas/auth.py` — add `UpdateMeRequest` here

## Setup (if starting fresh)
```bash
docker-compose up -d
uv sync
uv run alembic upgrade head
uv run python scripts/seed_test_data.py
uv run python scripts/import_nashville_csv.py
uv run python scripts/import_chicago_csv.py   # once you've written it
uv run uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

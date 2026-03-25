# Catherine - Check-ins, Gamification & Data Enrichment

## Status
Most of the original tasks were completed by Lucas. See `lucas.md` for what's done.

## Up Next

### Display Name Editing on Profile

Right now the profile page shows your display name but you can't change it. Add an edit flow.

**Backend — add a PATCH `/api/auth/me` endpoint in `app/api/routes/auth.py`:**
```python
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

Add `UpdateMeRequest` to `app/schemas/auth.py`:
```python
class UpdateMeRequest(BaseModel):
    display_name: str | None = None
```

**Frontend — edit mode on `ProfilePage.tsx`:**
- Add a small pencil icon next to the display name
- Clicking it swaps the name into an `<input>` with Save / Cancel buttons
- On save, call `PATCH /api/auth/me` with the new display name
- Update the JWT token in localStorage with the response (the backend returns a fresh token)
- Update the displayed name without reloading

### Leaderboard UI Polish
The leaderboard page exists but can be improved:

- Highlight the current logged-in user's row
- Add a gold/silver/bronze badge for ranks 1/2/3
- Show level next to username (e.g. "Lv. 4")
- Data comes from `GET /api/check-ins/leaderboard`

### Add Chicago (Data Task)

Nashville is the only city. Add Chicago as a second city.

**CSV columns required** (match Nashville exactly):

| Column | Description | Example |
|--------|-------------|---------|
| `name` | Short task name | `Deep Dish Standoff` |
| `category` | One of: `food`, `bars`, `museums`, `nature`, `street art`, `music`, `active`, `cafes`, `shopping`, `photo spots` | `food` |
| `description` | What the user does — fun and specific, 1-3 sentences | `Go to Lou Malnati's and order the deep dish...` |
| `verification_type` | `gps`, `photo`, or `both` | `photo` |
| `vibe_tags` | Comma-separated from: `foodie, adventurous, chill, cultural, nightlife, music, outdoors, photography, social, history, active, romantic` | `foodie,cultural` |
| `price_level` | 1 = free/cheap, 2 = $10-, 3 = $10-30, 4 = $30+ | `3` |
| `avg_duration_minutes` | Range like `45-60` or `60-90` | `45-60` |
| `lat` | Latitude from Google Maps (right-click → copy coordinates) | `41.8827` |
| `lng` | Longitude — must be negative for Chicago | `-87.6233` |

Aim for **30-40 tasks** covering a mix of categories and vibes.

**Steps to import:**
1. Create the CSV at `Gogo - chicago_template_tasks.csv` in the project root (same format as Nashville)
2. Add Chicago to the DB — run once in `uv run python`:
```python
from app.db.session import SessionLocal
from app.models import City
db = SessionLocal()
db.add(City(name="Chicago", state="IL", country="US", lat=41.8781, lng=-87.6298))
db.commit()
```
3. Duplicate `scripts/import_nashville_csv.py` → `scripts/import_chicago_csv.py`, change `CSV_PATH` and `City.name == "Chicago"`
4. Run: `uv run python scripts/import_chicago_csv.py`
5. Run: `uv run python scripts/assign_xp.py` to auto-calculate XP
6. Test by generating a route and selecting Chicago

## Key Files
- `app/api/routes/auth.py` — add `PATCH /me` here
- `app/schemas/auth.py` — add `UpdateMeRequest` here
- `app/models/user.py` — `display_name` field already exists
- `frontend/src/pages/ProfilePage.tsx` — edit UI goes here
- `frontend/src/pages/LeaderboardPage.tsx` — polish goes here

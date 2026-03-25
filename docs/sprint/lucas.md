# Lucas - AI Tuning & Data + Auth

## Completed

### AI & Data
- [x] Import Nashville CSV into `curated_tasks` — `scripts/import_nashville_csv.py`, 45 tasks live in DB
- [x] System prompt tuned in `app/services/ai_service.py` (time budgeting, vibe matching, creative titles)
- [x] Documented final `vibe_tags` and `categories` in `docs/sprint/csv.md`

### Auth
- [x] Build auth endpoints (register, login, JWT tokens) — `app/api/routes/auth.py`
- [x] Add auth middleware to protect all existing endpoints — `app/core/auth.py`, `Depends(get_current_user)`
- [x] Replace placeholder user in `app/api/routes/generate.py` with real auth
- [x] Wire auth into check-ins — `app/api/routes/checkins.py`, `app/schemas/checkins.py`

### XP System
- [x] XP formula and assignment script — `scripts/assign_xp.py`
- [x] `xp` column on tasks, `total_xp` + `level` on users
- [x] Award XP on successful check-in — `checkins.py` increments `user.total_xp`
- [x] `xp_to_level()` helper in `app/models/user.py`
- [x] `xp_earned`, `total_xp`, `level` returned in `CheckInResponse`

### Leaderboard
- [x] `GET /api/check-ins/leaderboard` — global XP leaderboard with rank, username, total_xp, level

### Tests
- [x] Auth tests — `tests/test_auth_api.py` (register, login, token validation)
- [x] Check-in tests — `tests/test_checkins_api.py` (16 tests: GPS/photo success, duplicate, wrong user, verification failures, progress, ownership)

### Cleanup
- [x] Updated README — removed stale TODOs, updated auth discussion section

---

## Up Next

### ~~Photo Storage (Cloudinary)~~ ✅ DONE
Wire up real photo storage so check-in photos are actually saved, not thrown away.

**Steps:**
1. `uv add cloudinary`
2. Add to `.env`: `CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name` (sign up at cloudinary.com, free tier is fine)
3. In `app/api/routes/checkins.py`, after verification passes (after line ~66), upload the photo:
```python
import cloudinary.uploader

photo_url = None
if request.photo_base64:
    upload_result = cloudinary.uploader.upload(
        f"data:image/jpeg;base64,{request.photo_base64}",
        folder="gogocity/checkins",
        public_id=str(request.instance_task_id),
        overwrite=True,
    )
    photo_url = upload_result["secure_url"]
```
4. Replace `photo_url=None` with `photo_url=photo_url` in the `CheckIn(...)` constructor

### UI — Per-Task Routing
Right now the route page is one long scrollable list. Build a per-task screen so users focus on one task at a time.

**Approach:**
- Add a route `/route/:instanceId/task/:taskIndex` in `App.tsx`
- New page `TaskPage.tsx` — shows one task, with Previous / Next buttons
- On the route overview (`RoutePage.tsx`), tapping a task navigates to its `TaskPage`
- `TaskPage` handles the Check In button and calls the same `CheckInModal`

### UI — Styling Pass
Polish the existing pages so it feels like a real app:
- `GeneratePage.tsx` — preference form needs better spacing, mobile-friendly inputs
- `HomePage.tsx` — active routes list, make cards feel more tappable
- `ProfilePage.tsx` — show level, XP bar, and avatar placeholder
- `LeaderboardPage.tsx` — rank badges, highlight current user's row
- General: consistent tap target sizes (min 44px), no text smaller than 11px, safe area padding on mobile

### CORS — Production Hardening
In `app/main.py`, change `allow_origins=["*"]` to only allow your frontend domain before going live.

---

## Key Files
- `app/api/routes/auth.py`
- `app/core/auth.py`
- `app/api/routes/checkins.py`
- `app/schemas/checkins.py`
- `app/models/user.py`
- `scripts/import_nashville_csv.py`
- `scripts/assign_xp.py`
- `tests/test_auth_api.py`
- `tests/test_checkins_api.py`

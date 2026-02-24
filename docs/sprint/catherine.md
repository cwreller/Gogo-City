# Catherine - Check-ins, Gamification & Data Enrichment

## Tasks

### Data Enrichment
- [ ] Enrich Nashville CSV - add `vibe_tags`, `price_level` (1-4), `avg_duration_minutes`, `lat`/`lng` for each of the 44 tasks
- [ ] CSV is at `nashville_template_tasks.csv` in the project root
- [ ] See `app/models/curated_task.py` for all the fields each task supports

### Check-ins
- [ ] Build POST `/api/check-ins` - create a check-in for an instance task
- [ ] GPS verification logic (compare user lat/lng to task lat/lng, pass if within X meters)
- [ ] Decide GPS radius threshold (50m? 100m? 200m?)
- [ ] Prevent duplicate check-ins (one check-in per instance task, already enforced in DB)

### Progress
- [ ] Build GET `/api/instances/{id}/progress` - return completed vs total tasks

### Gamification / XP
- [ ] Propose XP point values (per verification type? per task difficulty?)
- [ ] Add `xp` column to `curated_tasks` if we go with fixed XP per task
- [ ] Write Alembic migration for any new columns
- [ ] Build GET `/api/leaderboard` (if time)

## Key Files
- `app/models/checkin.py` (CheckIn model already exists)
- New: `app/api/routes/checkins.py`
- New: `app/services/checkin_service.py`

## Setup
```bash
git clone https://github.com/cwreller/Gogo-City.git
cd Gogo-City
docker-compose up -d
uv sync
cp .env.example .env
# OPENAI_API_KEY is optional for your tasks - check-ins/XP don't use AI
# Leave it blank or ask Lucas for the key if you want to test route generation
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## How Check-ins Work
- A `CheckIn` is tied to a specific `InstanceTask` (not a template task)
- Each instance task can only have one check-in (enforced by unique constraint)
- `verified_by` field tracks how it was verified (gps, photo, both)
- The `CheckIn` model is in `app/models/checkin.py`

## GPS Verification Reference
```python
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lng1, lat2, lng2):
    """Distance in meters between two lat/lng points."""
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))
```

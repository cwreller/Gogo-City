# Lucas - AI Tuning & Data + Auth

## Tasks

### AI & Data
- [ ] Import Nashville CSV into `curated_tasks` (map `location_based_tracking` → `gps`, `ai_photo_verification` → `photo`) **← blocked by Catherine finishing CSV enrichment**
- [ ] Test AI route generation with different preference combos (chill, nightlife, foodie, etc.)
- [ ] Tune the system prompt in `app/services/ai_service.py` if AI makes bad selections
- [ ] Document the final list of `vibe_tags` and `categories` we're using

### Auth
- [ ] Build auth endpoints (register, login, JWT tokens)
- [ ] Add auth middleware to protect existing endpoints
- [ ] Replace placeholder user in `app/api/routes/generate.py` with real auth

## Key Files
- `nashville_template_tasks.csv`
- `app/services/ai_service.py`
- `app/schemas/route_generation.py`
- `scripts/seed_test_data.py`
- New: `app/api/routes/auth.py`
- New: `app/core/auth.py`

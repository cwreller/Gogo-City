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

---

## Next Tasks

### Wire auth into check-ins (quick)
- [ ] Replace `request.user_id` body field in `app/api/routes/checkins.py` with `Depends(get_current_user)` — same pattern as the other routes
- [ ] Remove `user_id` from `CheckInRequest` schema in `app/schemas/checkins.py`

### XP System
The team decided on fixed XP per task (see README Team Discussions #2).

- [ ] Add `xp` column (int, default 10) to `curated_tasks`, `template_tasks`, `instance_tasks` — write Alembic migration
- [ ] Add `total_xp` (int, default 0) and `level` (int, default 1) columns to `users` — add to same migration
- [ ] Update `scripts/import_nashville_csv.py` to read `xp` from CSV (add xp column to CSV first)
- [ ] Award XP on successful check-in: in `checkins.py`, after creating CheckIn, increment `user.total_xp += task.xp`
- [ ] Auto-level logic: define thresholds (e.g. level = 1 + total_xp // 100) and update `user.level` on each XP award
- [ ] Return `total_xp` and `level` in the CheckInResponse so the frontend can show the update

### Leaderboard
- [ ] Build `GET /api/leaderboard` — return top N users sorted by `total_xp` (name, total_xp, level)
- [ ] Register leaderboard router in `app/api/__init__.py`

### Tests
- [ ] Write tests for `POST /api/check-ins` (success, duplicate, wrong user, GPS fail, no photo)
- [ ] Write tests for `GET /api/leaderboard`

### Cleanup
- [ ] Update README — remove stale TODOs ("Add real authentication", "Wipe curated_tasks") since both are done

---

## Key Files
- `app/api/routes/auth.py`
- `app/core/auth.py`
- `app/api/routes/checkins.py` ← needs auth wired in
- `app/schemas/checkins.py` ← needs user_id removed
- `app/models/user.py` ← needs total_xp, level
- `app/models/curated_task.py` ← needs xp
- `app/models/route.py` ← TemplateTask + InstanceTask need xp
- `scripts/import_nashville_csv.py`

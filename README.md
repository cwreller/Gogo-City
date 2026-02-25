# GoGoCity

A mobile app that generates personalized city routes (quests) based on user preferences.

---

## Quickstart

### 1. Install Docker

Download and install Docker Desktop:
- **Mac**: https://www.docker.com/products/docker-desktop/
- Click "Download for Mac" and run the installer
- Open Docker Desktop after installing (wait for it to say "Running")

### 2. Install uv (Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal.

### 3. Clone the repo

```bash
git clone https://github.com/cwreller/Gogo-City.git
cd Gogo-City
```

### 4. Run it

```bash
# Start the database
docker-compose up -d

# Install dependencies
uv sync

# Set up the database tables
uv run alembic upgrade head
```

### 5. Set up environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 6. Run the server

```bash
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000/docs to see the API.

---

## Useful Commands

```bash
# Stop the database
docker-compose down

# Add a new Python package
uv add <package-name>

# Run any Python command
uv run <command>
```

---

## Temp Files (delete before production)

These files are for development/demo only:

- `scripts/demo.py` - Demo script for class presentation
- `scripts/seed_test_data.py` - Seeds test data for Nashville
- `inspection/db-viewer.html` - Simple DB viewer (open in browser)

## TODO before launch

- [ ] Delete temp files listed above (scripts/demo.py, scripts/seed_test_data.py, inspection/db-viewer.html)
- [ ] Add `JWT_SECRET_KEY` to production environment (never use the default)
- [ ] XP system — add `xp` to tasks, `total_xp` + `level` to users, award on check-in
- [ ] Leaderboard endpoint — `GET /api/leaderboard`

---

## Team Discussions

### 1. Preferences Form - What fields do we need?

Current fields sent to AI:
- `city_id` (dropdown)
- `time_available_hours` (number)
- `budget` (low/medium/high/any)
- `vibe_tags` (multi-select)
- `dietary_restrictions` (multi-select)
- `group_size` (number)

**Questions:**
- What vibe tags do we want? (foodie, adventurous, chill, cultural, nightlife, romantic, outdoors, etc.)
- What dietary options? (vegetarian, vegan, gluten-free, halal, kosher, etc.)
- Any other preferences? (accessibility, kid-friendly, pet-friendly, walking distance only?)
- Should time be a slider or preset options (2hr, 4hr, full day)?

### 2. XP / Gamification System

**Decided:** Yes, we want XP. Users accumulate XP across all cities and routes as they explore.

**Approach:** Fixed XP per curated task (Option A). Each task gets an `xp` value in the CSV/database.
- Simpler, predictable, no extra AI tokens
- XP awarded on verified check-in
- Need to add `xp` column to CSV, `curated_tasks`, `template_tasks`, `instance_tasks`
- Need to add `total_xp` and `level` to `users`

**Levels:** Need to define XP thresholds (e.g. 0-100 = Level 1, 100-300 = Level 2, etc.)

**Leaderboard:** Global GoGoCity XP leaderboard, NOT per-route.
- Rewards overall exploration, not speedrunning a single route
- Could do daily/weekly/all-time tabs later

**XP Formula** (auto-calculated by `scripts/assign_xp.py`):
```
xp = duration_xp + price_bonus + verification_bonus

Duration:     2 XP per minute of midpoint (min 50). Works with any range.
              e.g. 20-30 -> 50 | 45-60 -> 104 | 60-90 -> 150 | 90-120 -> 210
Price bonus:  1 -> +0  | 2 -> +15  | 3 -> +30  | 4 -> +50
Verify bonus: gps -> +0 | photo -> +25 | both -> +50
```
Rerun `uv run python scripts/assign_xp.py` after updating CSV fields. Use `--dry-run` to preview.

**Level thresholds:** 0=L1, 200=L2, 500=L3, 1000=L4, 1750=L5, 2750=L6, 4000=L7, 5500=L8, 7500=L9, 10000=L10

**Still to decide:**
- Badges/achievements? (first route, first city, 10 check-ins, etc.) — probably post-MVP
- Streaks? (complete a route every week) — probably post-MVP

### 3. Authentication

**Done:** Email/password with JWT tokens (`POST /auth/register`, `POST /auth/login`). All endpoints protected via `Bearer` token.

Future: social login (Google/Apple) can be added by swapping `app/core/auth.py` — the rest of the codebase won't need to change.

### 4. Route Task Ordering

Currently: Tasks are unordered (user does them in any order)
- Should AI order tasks geographically (minimize travel)?
- Should AI order by time-of-day (brunch spot first, bar last)?
- Or keep it flexible and let users choose?

### 5. Editing Generated Routes

- Can users edit a route after AI generates it? (add/remove/reorder tasks)
- If yes, do we need a route editor UI?
- Or is it "generate and go" only for MVP?

### 6. AI Cost at Scale

- Current model: gpt-4o (~$5-15 per 1M tokens)
- At scale with 1000s of users, costs add up
- Do we cache similar preference combos?
- Switch to cheaper model (gpt-4o-mini) for some users?

### 7. Public Template Library?

Current plan: Routes are either AI-generated for you or shared directly by a friend. No public browsing.

**Argument for a public library:**
- Users could run the same route and compare scores/times ("Who completed the Nashville Foodie Challenge faster?")
- Leaderboard per route = real apples-to-apples competition
- Community feel, replay value, people try popular routes

**Argument against:**
- Reduces the "personalized" feel (the whole point is AI picks tasks for YOU)
- More to build (browsing UI, sorting, moderation)
- Could wait until we see how people actually use sharing first
- Do we really need people rushing to complete something if time is our main quantifier? That makes it less enjoyable potetntially 

**Note:** The `is_public` field already exists on `RouteTemplate` (default false), so the data model supports this whenever we decide to flip it on. Not needed for MVP.

### 8. Photo Verification Accuracy vs Cost

Currently using `detail: "low"` in OpenAI Vision calls for photo verification. This uses ~85 tokens per image (cheap) but may miss fine details.

Options:
- `"low"` (current): Fast, cheap, good for obvious matches (storefront signs, food plates)
- `"auto"`: Let OpenAI decide based on image size. Moderate cost.
- `"high"`: Best accuracy, analyzes image tiles. More expensive per check-in.

If users complain about false rejections, bump to `"auto"` first. Monitor token usage before going to `"high"`.

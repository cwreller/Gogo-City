# Trey - Route Instances & Sharing

## Tasks

### Route Instances
- [ ] Build POST `/api/instances` - import a template into a personal route instance
- [ ] Build GET `/api/instances` - list my route instances
- [ ] Build GET `/api/instances/{id}` - get a single instance with tasks and progress
- [ ] Instance snapshotting logic (copy template tasks into instance tasks on import)
- [ ] Progress tracking (calculate completed vs total tasks)

### Sharing
- [ ] Build GET `/api/routes/share/{share_code}` - preview a shared route
- [ ] Build POST `/api/routes/import/{share_code}` - import a shared route into your account
- [ ] Make sure importing creates an independent instance (no shared progress)

### Stretch
- [ ] Start thinking about a second city?

## Key Files
- `app/models/route.py` (RouteInstance, InstanceTask models already exist)
- New: `app/api/routes/instances.py`
- New: `app/api/routes/sharing.py`
- New: `app/services/instance_service.py`

## Setup

### 1. Clone the repo (don't fork)
```bash
git clone https://github.com/cwreller/Gogo-City.git
cd Gogo-City
```

### 2. Create your branch
```bash
git checkout -b trey/instances-and-sharing
```

### 3. Install everything
```bash
docker-compose up -d
uv sync
cp .env.example .env
# OPENAI_API_KEY is optional for your tasks - instances/sharing don't use AI
# Leave it blank or ask Lucas for the key if you want to test route generation
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

### 4. When you're ready to push
```bash
git add .
git commit -m "description of what you did"
git push -u origin trey/instances-and-sharing
```
Then open a Pull Request on GitHub to merge into `main`.

## How It Works
- `RouteTemplate` = the shareable plan (has a `share_code`)
- `RouteInstance` = a user's personal copy (created when they import a template)
- `InstanceTask` = snapshot of each task, copied from `TemplateTask` at import time
- Each instance tracks progress independently

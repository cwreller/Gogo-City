# GoGoCity

A mobile app that generates personalized city routes (quests) based on user preferences.

## Setup

```bash
# Start Postgres
docker-compose up -d

# Install dependencies (uses uv)
uv sync

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run uvicorn app.main:app --reload
```

## Common Commands

```bash
# Add a dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Run any command in the venv
uv run <command>

# Stop Postgres
docker-compose down
```

## Features

- Personalized route generation based on budget, distance, time, and vibe preferences
- Shareable route templates
- Independent progress tracking per user
- Check-in system for stops

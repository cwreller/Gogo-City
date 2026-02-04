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

- [ ] Wipe `curated_tasks` table - current data is test/seed data, need hand-picked tasks
- [ ] Add real authentication (currently using placeholder user)
- [ ] Delete temp files listed above

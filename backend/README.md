# Smart Room Digital Twin - Backend (skeleton)

This folder contains a minimal FastAPI backend scaffold to support the frontend.

Quick start (macOS / zsh):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Next steps:
- Implement decision engine and agent integrations (LangChain, OpenAI/Anthropic/Gemini)
- Add RAG ingestion and vector DB
- Add MQTT / IoT integration
- Add RBAC (users) and tests

Postgres setup and seeding
1. Install Postgres (macOS, Homebrew):

```bash
brew install postgresql
brew services start postgresql
psql -U postgres -c "CREATE DATABASE smartroom;"
```

2. Initialize schema using the provided SQL (or run alembic later):

```bash
cd backend
psql -U postgres -d smartroom -f db_init.sql
```

3. Or use the Python seed script (uses DATABASE_URL in `.env` or `app/config.py`):

```bash
source .venv/bin/activate
python seed_db.py
```

4. Run the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Notes:
- If you use a hosted Postgres or different credentials, set `DATABASE_URL` in `.env` before running.
- Alembic is included in `requirements.txt` for future migrations; I didn't initialize an alembic env automatically to keep the scaffold minimal.

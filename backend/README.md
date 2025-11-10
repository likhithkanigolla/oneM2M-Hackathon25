# Smart Room Digital Twin - Backend

This FastAPI backend provides a complete API for the Smart Room Digital Twin system with PostgreSQL database integration.

## Features
- **Complete REST API** for rooms, devices, agents, scenarios, SLOs, users, and analytics
- **PostgreSQL database** with full schema and relationships
- **Seed data** with realistic smart room configurations
- **Database migrations** for schema updates
- **AI agent management** with configurable weights and RAG sources
- **Scenario management** with priority levels and impact tracking
- **User management** with role-based access control
- **Analytics and decision logging** for AI decision tracking

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

4. **For existing databases**, run migration to add new schema features:

```bash
source .venv/bin/activate
python migrate_db.py
```

This will:
- Add `priority`, `trigger`, `impact` columns to scenarios table
- Add `full_name`, `role`, `is_active`, `assigned_rooms`, `created_at` columns to users table  
- Update existing data with proper values

5. Run the server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Notes:
- If you use a hosted Postgres or different credentials, set `DATABASE_URL` in `.env` before running.
- Alembic is included in `requirements.txt` for future migrations; I didn't initialize an alembic env automatically to keep the scaffold minimal.

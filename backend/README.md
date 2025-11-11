# Smart Building Management System Backend

## 🤖 AI-Powered Digital Twin

This backend powers an **intelligent building management system** with LLM agents that make real-time decisions based on SLOs, sensor data, and occupancy patterns. The system uses **Google Gemini API** for free AI-powered decision making.

## ✨ Key Features

### 🧠 **Multi-Agent AI Decision Engine**
- **6 specialized LLM agents**: Security, Comfort, Energy, Emergency, Environmental, Occupancy
- **Conflict resolution**: Priority weighting, majority vote, manual escalation
- **Real-time decisions** based on sensor data and SLO requirements
- **Audit trail** with AI reasoning explanations

### 🎯 **SLO-Driven Management**  
- **Global SLOs**: Admin-defined building-wide policies (e.g., "minimum lighting for surveillance")
- **Room SLOs**: Operator-specific requirements (e.g., "meeting rooms at 22°C") 
- **Dynamic balancing**: AI agents optimize competing priorities automatically

### 🌡️ **IoT Integration**
- Real-time sensor data processing (temperature, humidity, CO2, occupancy)
- Mock data generation for testing and development
- Environmental scoring and air quality indexing

### 👥 **Role-Based Access Control**
- **Admins**: Global SLO management, system oversight
- **Operators**: Room-specific SLO configuration, device control
- **Audit logs**: Complete decision history with AI explanations

## 🚀 Quick Start with LLM Integration

### 1. **Get Free Google AI API Key**
```bash
# Visit Google AI Studio (free tier available)
open https://aistudio.google.com/app/apikey
```

### 2. **Automated Setup**
```bash
# Run the setup script
./setup_llm.sh
```

### 3. **Manual Setup** (Alternative)
```bash
# Install dependencies  
pip install -r requirements.txt
pip install google-generativeai httpx

# Configure environment
cp .env.example .env
# Add GOOGLE_API_KEY=your_key_here to .env

# Setup database
python migrate_db.py
python seed_db.py

# Start server
uvicorn app.main:app --reload
```

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

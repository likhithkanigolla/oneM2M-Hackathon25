# Frontend (UI) — oneM2M Hackathon25

This folder contains the React frontend for the Digital Twin / Smart Building demo app.

Purpose
- Provide dashboards for Analytics, Rooms, Agents, and LLM insights.
- Consume backend APIs served by the FastAPI backend at `/api/*`.

Quick start (development)
1. Install dependencies
```bash
cd frontend
# using npm
npm install
# or using pnpm / yarn if you prefer
```

2. Run the dev server
```bash
npm run dev
# open http://localhost:5173 (Vite default)
```

Backend integration (local)
- The frontend expects a backend API base URL at `VITE_API_BASE` (used in the stores). By default the app uses an environment variable `VITE_API_BASE` at build/dev time.
- Example when running backend locally on port 8000:
```bash
export VITE_API_BASE=http://localhost:8000
npm run dev
```

LLM and rate-limiting notes
- The backend integrates with Google Gemini for LLM-driven agent reasoning. Gemini has strict per-project rate limits (default free-tier: 10 generate requests / minute per model).
- The backend includes a process-local async rate limiter configured by default to 9 requests/minute to avoid hitting the 10/min quota. The setting can be overridden with the environment variable `LLM_MAX_REQUESTS_PER_MINUTE` on the backend process.
- Important: the limiter is process-local. If you run multiple backend workers (uvicorn with `--workers`), or additional hosts using the same Gemini key, you will still exceed project-wide quotas. For multi-worker deployments use a centralized limiter (Redis) — see backend notes.

Frontend developer notes
- Pages that show data from the backend: `Analytics`, `RoomDetails`, `LLMInsights`, `Agents`, `SLOConfig`.
- Stores (Zustand) are in `frontend/src/store/*` and provide fetch functions that call the backend `VITE_API_BASE` endpoints. The frontend pages use sensible fallbacks when the backend is not available.
- When testing without Gemini (or to avoid consuming quota), either:
  - Do not set `GOOGLE_API_KEY` in the backend environment, or
  - Set `LLM_MAX_REQUESTS_PER_MINUTE=0` (backend will fall back to rule-based agents), or
  - Run the backend in a single process and leave the limiter default at 9/min.

Recommended workflow for end-to-end testing
1. Start and seed the backend (see `/backend/README.md`). Ensure dependencies are installed in the backend venv and the database is seeded.
2. Export `VITE_API_BASE` pointing at the running backend.
3. Start the frontend: `npm run dev` and open the UI.

Helpful backend endpoints (examples)
- `GET /api/rooms/` — list rooms
- `GET /api/slos/` — list SLOs
- `GET /api/analytics/` — historical analytics data
- `GET /api/agents/` — list configured agents
- `POST /api/decisions/coordinate` — trigger a coordination run (backend handles periodic runs too)

Contributing
- Keep UI changes small and test with backend running. If you add pages that request LLM-driven endpoints, be mindful of quota and use the backend's rate limiter.

Contact / Next steps
- If you want, I can add simple loading skeletons to the pages or wire additional endpoints into the stores. I can also implement a Redis-backed global rate limiter for the backend to enforce Gemini quotas across multiple processes.

---
`frontend/` — React + Vite app (TypeScript). Build artifacts are produced by the Vite toolchain.

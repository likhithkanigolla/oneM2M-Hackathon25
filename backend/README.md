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

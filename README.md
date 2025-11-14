
# Digital Twin — Smart Building Demo (oneM2M Hackathon 2025)

This repository contains the code for a smart‑building digital twin demo created for the oneM2M Hackathon 2025. The project demonstrates a decision‑making system that combines deterministic rules and optional LLM‑based agents to manage rooms, devices, comfort, energy, occupancy and safety policies.

## Table of Contents

- [Digital Twin — Smart Building Demo (oneM2M Hackathon 2025)](#digital-twin--smart-building-demo-onem2m-hackathon-2025)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Key Features](#key-features)
  - [Architecture](#architecture)
  - [Agents and Responsibilities](#agents-and-responsibilities)
  - [Repository Layout](#repository-layout)
  - [Software Setup (Summary)](#software-setup-summary)
  - [Configuration](#configuration)
  - [Data and Seed Content](#data-and-seed-content)
  - [Running the Demo (Quick)](#running-the-demo-quick)
  - [API \& Frontend Notes](#api--frontend-notes)
  - [Testing and Health Checks](#testing-and-health-checks)
  - [Development Tips](#development-tips)
  - [Contribution \& Contact](#contribution--contact)
  - [License](#license)

## Project Overview

This project simulates a building management environment where autonomous agents monitor sensor data and control devices to meet multiple objectives (comfort, energy efficiency, security, and safety). Agents can operate in two modes:

- LLM-driven: When cloud LLM credentials are available (e.g., Google Generative AI), agents use the LLM to generate decisions and reasoning.
- Fallback/rule-driven: When LLM access is not configured, agents use deterministic rules so the demo remains deterministic and robust for live presentations.

The system is built as a classic web application: a backend that hosts APIs, agent logic and a database, and a frontend single‑page application that visualizes rooms, agents, and insights.

## Key Features

- Modular agent framework supporting multiple specialist agents.
- Transparent decision recording (decisions, reasoning, scores, confidence).
- Robust fallback behavior so demos work without external LLM access.
- Seeded sample environment (rooms, sensors, devices, SLOs) for predictable demos.
- Frontend UI showing rooms, agent controls, and decision history.

## Architecture

- Backend (Python): hosts APIs, agent implementations, decision coordination, LLM client integration, and persistence.
- Frontend (TypeScript + Vite): single‑page app for visualizing state, toggling agents, and viewing analytics.
- Database (relational, PostgreSQL recommended): stores rooms, devices, agents, SLOs, decision logs.
- Optional external LLM service: used by `GeminiLLMClient` when `GOOGLE_API_KEY` (or other configured key) is present.

Components and where to find them:

- Backend application: `backend/app` (main modules: `main.py`, `agents/`, `services/`, `routers/`).
- Agent definitions & configuration: `backend/app/agents/` (`agent_config.py`, `llm_agents.py`, `base_agent.py`, `gemini_client.py`).
- DB schema & seed: `backend/db_init.sql`, `backend/seed_db.py`, and `backend/db_seed.sql`.
- Frontend app: `frontend/src` (pages, components, store).

## Agents and Responsibilities

The system defines several specialist agents. Each agent focuses on a specific domain and has configuration in `backend/app/agents/agent_config.py`.

- Security Agent — ensures surveillance and device readiness (lighting for cameras, access control, security devices).
- Emergency (Emergency Response) Agent — handles safety and crisis protocols; overrides other agents during emergencies.
- Environmental Agent — monitors air quality, humidity and ventilation.
- Occupancy Agent — optimizes room utilization and adjusts systems based on occupancy.
- Comfort Agent — optimizes temperature, lighting and air circulation for occupant wellbeing.
- Energy Agent — minimizes energy consumption while respecting critical constraints.

All agents implement a common interface (`BaseAgent` in `backend/app/agents/base_agent.py`) and may use the `GeminiLLMClient` (`backend/app/agents/gemini_client.py`) to ask a large language model for decisions. If the LLM client is unavailable, each agent uses a built‑in fallback decision routine.

## Repository Layout

Top-level layout (abridged):

```
README.md
setup_llm.sh
backend/
	app/
		agents/
		api/
		models/
		routers/
		services/
	seed_db.py
	db_init.sql
frontend/
	src/
tests/
docs/
```

Refer to the repository root and the `backend/app/agents` folder for agent-specific prompts and configuration.

## Software Setup (Summary)

This README provides both a plain‑language summary (what we did for the hackathon) and an actionable quick start (commands) for reproducibility.

Plain language summary for reports:

- Prerequisites: a recent Python runtime and a modern JavaScript runtime. A relational DB is needed to persist demo state. An LLM API key is optional.
- Configuration: supply database connection details and any LLM API keys through environment settings or configuration files in the backend and frontend.
- Initial state: the repository contains schema and seed scripts that create rooms, sensors and agents for a realistic demo environment.
- Execution: start the backend service and the frontend web app. The frontend displays rooms and agents and the backend runs agents which make decisions and store logs.

If you want runnable instructions (recommended for reproducibility and for the team), see the "Running the Demo (Quick)" section below.

## Configuration

Key configuration points and files to be aware of:

- Backend settings and environment variables: the backend reads settings used throughout the app (database connection, `GOOGLE_API_KEY` for LLMs, etc.). See `backend/app/config.py` for exact names used in your deployment.
- Agent prompts: per‑agent prompt templates live under `backend/app/agents/prompts/` (for example `security_agent_prompt.txt`).
- Sample data and migrations: `backend/db_init.sql`, `backend/seed_db.py`, and `backend/db_seed.sql`.

Design notes:

- The system tries to initialize the Gemini LLM client once per process; if the SDK or keys are missing the system logs the condition and agents fall back to rule-based logic.
- A global LLM rate‑limiter is available in `backend/app/agents/llm_rate_limiter.py` to throttle API calls when LLMs are enabled.

## Data and Seed Content

The repository includes seed data to populate rooms, devices, agents and SLOs so the demo is immediately meaningful. Seed scripts and SQL files live in the `backend/` directory. Use these to create a reproducible initial demo state for judges and testing.

## Running the Demo (Quick)

Below is a reproducible quick start that the development team used during the hackathon. These commands assume a POSIX shell (zsh/bash) and typical development environments. Adjust paths and virtual environments as needed.

1. Prepare backend dependencies and environment.
2. Initialize or connect to a database and load the provided schema and sample data.
3. Start the backend server and the frontend dev server.

Note: for exact commands and environment details consult the project scripts: `setup_llm.sh`, `backend/requirements.txt` and `frontend/package.json`.

## API & Frontend Notes

- Backend APIs expose agent management, room state, device control, decision logs, and analytics. The main backend entry point is `backend/app/main.py`.
- Frontend pages and components that are relevant for demos live under `frontend/src/pages/` and `frontend/src/components/`. Agent UI components are in `frontend/src/components` and the store is in `frontend/src/store`.

Example demo interactions:

- View Rooms / Dashboard to establish the initial environment state.
- Enable an agent (e.g., `Energy Saver`) to demonstrate its behavior and show decisions in the UI.
- Show Decision history and LLM reasoning (when available) to highlight explainability.

## Testing and Health Checks

The repository contains automated checks and integration tests useful for verifying the environment:

- Python LLM integration checks and unit tests are in `tests/` (for example `test_llm_integration.py`).
- A small script, `check_gemini_state.py`, helps validate LLM client availability and configuration on the host.

Before a live demo we verified:

- Backend can connect to the database and returns healthy API responses.
- Frontend successfully loads and communicates with the backend.
- At least one agent runs in fallback mode when LLMs are not configured.

## Development Tips

- Agent behaviour is intentionally modular. To customize an agent, edit the prompt templates in `backend/app/agents/prompts/` or modify the fallback logic in `backend/app/agents/llm_agents.py`.
- To add a new agent type, extend `AgentType` and register the configuration in `backend/app/agents/agent_config.py`, then implement the agent following the `BaseAgent` interface.
- Keep LLM prompts concise and validate JSON-only responses from the model; the `GeminiLLMClient` contains parsing helpers.

## Contribution & Contact

If you want to contribute or reproduce the demo, please:

- Follow the repository structure and add tests for new behaviour.
- Keep agent prompts and decision formats stable (JSON schema in `gemini_client.py`).

For questions about the implementation or to request a demo, contact the project lead on the hackathon team.

## License

This repository is submitted for the oneM2M Hackathon 2025. 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.rooms import router as rooms_router
from app.api.routes.devices import router as devices_router
from app.api.routes.agents import router as agents_router
from app.api.routes.slos import router as slos_router
from app.api.routes.scenarios import router as scenarios_router
from app.api.routes.users import router as users_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.llm_test import router as llm_test_router
from app.database import engine, Base
# ensure models are imported so metadata is registered
import app.models  # noqa: F401

app = FastAPI(title="Smart Room Digital Twin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(rooms_router, prefix="/api/rooms", tags=["rooms"])
app.include_router(devices_router, prefix="/api/devices", tags=["devices"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(slos_router, prefix="/api/slos", tags=["slos"])
app.include_router(scenarios_router, prefix="/api/scenarios", tags=["scenarios"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(llm_test_router)

@app.on_event("startup")
async def startup():
    # create tables
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Smart Room Digital Twin API - Now with LLM Intelligence!"}

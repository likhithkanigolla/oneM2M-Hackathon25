from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.rooms import router as rooms_router
from app.database import engine, Base
# ensure models are imported so metadata is registered
import app.models  # noqa: F401

app = FastAPI(title="Smart Room Digital Twin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router, prefix="/api/rooms", tags=["rooms"])

@app.on_event("startup")
async def startup():
    # create tables
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Smart Room Digital Twin API"}

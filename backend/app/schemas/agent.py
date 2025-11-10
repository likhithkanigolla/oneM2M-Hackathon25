from pydantic import BaseModel
from typing import List, Optional, Any

class AgentBase(BaseModel):
    id: str
    name: str
    goal: Optional[str] = None
    rag_sources: Optional[List[str]] = []
    active: Optional[bool] = True
    endpoint: Optional[str] = None
    weight: Optional[float] = 0.33

    class Config:
        orm_mode = True

class AgentCreate(BaseModel):
    id: str
    name: str
    goal: Optional[str] = None
    rag_sources: Optional[List[str]] = []
    active: Optional[bool] = True
    endpoint: Optional[str] = None
    weight: Optional[float] = 0.33

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    rag_sources: Optional[List[str]] = None
    active: Optional[bool] = None
    endpoint: Optional[str] = None
    weight: Optional[float] = None

    class Config:
        orm_mode = True
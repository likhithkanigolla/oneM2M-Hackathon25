from pydantic import BaseModel
from typing import Optional, Any

class ScenarioBase(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    active: Optional[bool] = False
    config: Optional[Any] = None
    priority: Optional[str] = "Medium"
    trigger: Optional[str] = None
    impact: Optional[str] = None

    class Config:
        orm_mode = True

class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    active: Optional[bool] = False
    config: Optional[Any] = None
    priority: Optional[str] = "Medium"
    trigger: Optional[str] = None
    impact: Optional[str] = None

class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    config: Optional[Any] = None
    priority: Optional[str] = None
    trigger: Optional[str] = None
    impact: Optional[str] = None

    class Config:
        orm_mode = True
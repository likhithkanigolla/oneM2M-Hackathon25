from pydantic import BaseModel
from typing import Optional, Any

class SLOBase(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    metric: Optional[str] = None
    config: Optional[Any] = None

    class Config:
        from_attributes = True

class SLOCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    metric: Optional[str] = None
    config: Optional[Any] = None

class SLOUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    metric: Optional[str] = None
    config: Optional[Any] = None

    class Config:
        from_attributes = True
from pydantic import BaseModel
from typing import Optional, Any

class SLOBase(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    metric: Optional[str] = None
    weight: Optional[float] = 0.1
    active: Optional[bool] = True
    config: Optional[Any] = None
    created_by: str
    is_system_defined: Optional[bool] = False

    class Config:
        from_attributes = True

class SLOCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    metric: Optional[str] = None
    weight: Optional[float] = 0.1
    active: Optional[bool] = True
    config: Optional[Any] = None
    is_system_defined: Optional[bool] = False

class SLOUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    metric: Optional[str] = None
    weight: Optional[float] = None
    active: Optional[bool] = None
    config: Optional[Any] = None

    class Config:
        from_attributes = True

class SLOResponse(SLOBase):
    id: int
    
    class Config:
        from_attributes = True
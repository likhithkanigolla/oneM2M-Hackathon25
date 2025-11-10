from pydantic import BaseModel
from typing import List, Optional, Any

class DeviceBase(BaseModel):
    id: Optional[int] = None
    name: str
    type: Optional[str] = None
    status: Optional[str] = "OFF"
    room_id: Optional[int] = None
    services: Optional[List[Any]] = []

    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    name: str
    type: Optional[str] = None
    status: Optional[str] = "OFF"
    room_id: int
    services: Optional[List[Any]] = []

    class Config:
        from_attributes = True

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    services: Optional[List[Any]] = None

    class Config:
        from_attributes = True

class DeviceResponse(DeviceBase):
    id: int

    class Config:
        from_attributes = True
from pydantic import BaseModel
from typing import List, Optional, Any

class DeviceBase(BaseModel):
    id: Optional[int]
    name: str
    type: Optional[str]
    status: Optional[str]
    services: Optional[Any]

    class Config:
        from_attributes = True

class RoomBase(BaseModel):
    id: Optional[int]
    name: str
    gsi: Optional[float]
    aq: Optional[int]
    temp: Optional[float]
    occupancy: Optional[int]
    position: Optional[Any]
    devices: Optional[List[DeviceBase]] = []

    class Config:
        from_attributes = True

class RoomCreate(BaseModel):
    name: str
    gsi: Optional[float] = 0.0
    aq: Optional[int] = 80
    temp: Optional[float] = 22.0
    occupancy: Optional[int] = 0
    position: Optional[Any] = None

    class Config:
        from_attributes = True

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    gsi: Optional[float] = None
    aq: Optional[int] = None
    temp: Optional[float] = None
    occupancy: Optional[int] = None
    position: Optional[Any] = None

    class Config:
        from_attributes = True

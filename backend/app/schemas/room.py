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

class RoomCreate(RoomBase):
    name: str

class RoomUpdate(BaseModel):
    gsi: Optional[float]
    aq: Optional[int]
    temp: Optional[float]
    occupancy: Optional[int]
    position: Optional[Any]

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "operator"
    is_active: Optional[bool] = True
    assigned_rooms: Optional[List[int]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "operator"
    is_active: Optional[bool] = True
    assigned_rooms: Optional[List[int]] = None
    password: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    assigned_rooms: Optional[List[int]] = None

    class Config:
        from_attributes = True
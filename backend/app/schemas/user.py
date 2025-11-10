from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    id: Optional[int] = None
    username: str
    email: Optional[str] = None
    is_admin: Optional[bool] = False

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = False

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
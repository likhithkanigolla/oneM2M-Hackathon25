from pydantic import BaseModel
from typing import Optional, List

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "operator"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    assigned_rooms: Optional[List[int]] = None

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "operator"

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    role: str
    assigned_rooms: Optional[List[int]] = None
    
    class Config:
        from_attributes = True
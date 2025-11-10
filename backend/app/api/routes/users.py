from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserBase, UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[UserBase])
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserBase)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserBase)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    # Check if user already exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Simple password handling (in production, hash the password)
    user_data = user.dict()
    if user_data.get('password'):
        user_data['hashed_password'] = user_data.pop('password')  # Simple assignment for demo
    
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserBase)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
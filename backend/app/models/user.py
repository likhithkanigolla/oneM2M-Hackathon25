from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(String, default="operator")  # admin, operator
    is_active = Column(Boolean, default=True)
    assigned_rooms = Column(JSON, nullable=True)  # List of room IDs
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "assigned_rooms": self.assigned_rooms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

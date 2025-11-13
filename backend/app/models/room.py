from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    gsi = Column(Float, default=0.0)
    aq = Column(Integer, nullable=True)
    temp = Column(Float, nullable=True)
    occupancy = Column(Integer, nullable=True)
    position = Column(JSON, nullable=True)
    last_coordinated_at = Column(DateTime, nullable=True)
    last_coordination_summary = Column(JSON, nullable=True)

    devices = relationship("Device", back_populates="room", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="room", cascade="all, delete-orphan")
    decision_logs = relationship("DecisionLog", back_populates="room")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gsi": self.gsi,
            "aq": self.aq,
            "temp": self.temp,
            "occupancy": self.occupancy,
            "position": self.position,
            "last_coordinated_at": self.last_coordinated_at.isoformat() if self.last_coordinated_at else None,
            "last_coordination_summary": self.last_coordination_summary,
            "devices": [d.to_dict() for d in self.devices],
        }

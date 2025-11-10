from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class DeviceStatus(str, enum.Enum):
    ON = "ON"
    OFF = "OFF"

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFF)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    services = Column(JSON, nullable=True)

    room = relationship("Room", back_populates="devices")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status.value if self.status else None,
            "services": self.services,
        }

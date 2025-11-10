from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class DecisionLog(Base):
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_id = Column(String, ForeignKey("agents.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    decision = Column(String)
    reasoning = Column(String, nullable=True)
    comfort_score = Column(Float, nullable=True)
    energy_score = Column(Float, nullable=True)
    reliability_score = Column(Float, nullable=True)
    context = Column(JSON, nullable=True)

    room = relationship("Room", back_populates="decision_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "agent_id": self.agent_id,
            "room_id": self.room_id,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "comfort_score": self.comfort_score,
            "energy_score": self.energy_score,
            "reliability_score": self.reliability_score,
            "context": self.context,
        }

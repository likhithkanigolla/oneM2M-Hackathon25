from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=False)
    config = Column(JSON, nullable=True)
    priority = Column(String, default="Medium")  # Low, Medium, High, Critical
    trigger = Column(String, nullable=True)     # What triggers this scenario
    impact = Column(String, nullable=True)      # Expected impact description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "active": self.active,
            "config": self.config,
            "priority": self.priority,
            "trigger": self.trigger,
            "impact": self.impact,
        }

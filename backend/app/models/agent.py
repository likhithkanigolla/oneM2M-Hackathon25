from sqlalchemy import Column, String, Float, Boolean, JSON
from app.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    goal = Column(String, nullable=True)
    rag_sources = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    endpoint = Column(String, nullable=True)
    weight = Column(Float, default=0.33)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "rag_sources": self.rag_sources,
            "active": self.active,
            "endpoint": self.endpoint,
            "weight": self.weight,
        }

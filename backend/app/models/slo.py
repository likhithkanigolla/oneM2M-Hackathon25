from sqlalchemy import Column, Integer, String, Float, JSON
from app.database import Base


class SLO(Base):
    __tablename__ = "slos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_value = Column(Float, nullable=True)
    metric = Column(String, nullable=True)
    config = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value,
            "metric": self.metric,
            "config": self.config,
        }

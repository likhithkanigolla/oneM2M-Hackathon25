from sqlalchemy import Column, Integer, String, Float, JSON, Boolean
from app.database import Base


class SLO(Base):
    __tablename__ = "slos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_value = Column(Float, nullable=True)
    metric = Column(String, nullable=True)
    weight = Column(Float, default=0.1)  # Weight for SLO importance
    active = Column(Boolean, default=True)  # Whether SLO is active
    config = Column(JSON, nullable=True)
    created_by = Column(String, nullable=False)  # Username who created the SLO
    is_system_defined = Column(Boolean, default=False)  # True for admin-defined SLOs

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value,
            "metric": self.metric,
            "weight": self.weight,
            "active": self.active,
            "config": self.config,
            "created_by": self.created_by,
            "is_system_defined": self.is_system_defined,
        }

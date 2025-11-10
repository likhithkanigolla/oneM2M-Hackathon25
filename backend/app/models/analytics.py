from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class HistoricalMetric(Base):
    __tablename__ = "historical_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    metric_type = Column(String(50))  # "comfort", "energy", "reliability"
    value = Column(Float)
    
    room = relationship("Room", back_populates="metrics")

class SystemEvent(Base):
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    event_type = Column(String(100))
    description = Column(Text)
    impact = Column(Text)
    
    room = relationship("Room")

class SLOPerformance(Base):
    __tablename__ = "slo_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    slo_id = Column(Integer, ForeignKey("slos.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    current_value = Column(Float)
    target_value = Column(Float)
    performance_score = Column(Float)  # 0.0 to 1.0
    
    slo = relationship("SLO")
    room = relationship("Room")
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HistoricalMetricSchema(BaseModel):
    id: int
    timestamp: datetime
    room_id: int
    metric_type: str
    value: float
    
    class Config:
        from_attributes = True

class SystemEventSchema(BaseModel):
    id: int
    timestamp: datetime
    room_id: int
    event_type: str
    description: str
    impact: str
    
    class Config:
        from_attributes = True

class SLOPerformanceSchema(BaseModel):
    id: int
    slo_id: int
    room_id: int
    timestamp: datetime
    current_value: float
    target_value: float
    performance_score: float
    
    class Config:
        from_attributes = True

class HistoricalDataPoint(BaseModel):
    time: str
    comfort: float
    energy: float
    reliability: float

class RecentEvent(BaseModel):
    time: str
    room: str
    event: str
    impact: str

class AgentDecision(BaseModel):
    time: str
    agent: str
    decision: str
    confidence: float
    reasoning: str
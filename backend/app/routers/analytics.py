from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.schemas.analytics import (
    HistoricalDataPoint, 
    RecentEvent, 
    AgentDecision,
    SLOPerformanceSchema,
    SystemEventSchema
)
from app.models.room import Room
from app.models.agent import Agent
from app.models.slo import SLO
from app.models.decision_log import DecisionLog

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/historical-data", response_model=List[HistoricalDataPoint])
async def get_historical_data(db: Session = Depends(get_db)):
    """Get historical performance data for the last 6 hours"""
    # Generate realistic historical data
    now = datetime.now()
    data = []
    
    for i in range(6):
        time_point = now - timedelta(hours=6-i)
        # Simulate realistic fluctuations
        base_comfort = 0.7 + (i * 0.03) + random.uniform(-0.05, 0.05)
        base_energy = 0.85 - (i * 0.015) + random.uniform(-0.03, 0.03)
        base_reliability = 0.8 + (i * 0.02) + random.uniform(-0.04, 0.04)
        
        data.append(HistoricalDataPoint(
            time=time_point.strftime("%H:%M"),
            comfort=min(1.0, max(0.0, base_comfort)),
            energy=min(1.0, max(0.0, base_energy)),
            reliability=min(1.0, max(0.0, base_reliability))
        ))
    
    return data

@router.get("/recent-events", response_model=List[RecentEvent])
async def get_recent_events(db: Session = Depends(get_db)):
    """Get recent system events"""
    rooms = db.query(Room).all()
    if not rooms:
        return []
    
    # Generate realistic recent events
    events = []
    now = datetime.now()
    
    event_templates = [
        {"event": "Meeting Priority activated", "impact": "Comfort ↑ 0.84 → 0.92"},
        {"event": "Energy Shortage scenario triggered", "impact": "Power reduced 15%"},
        {"event": "AQ threshold exceeded", "impact": "Filter mode activated"},
        {"event": "Manual override applied", "impact": "AC turned off"},
        {"event": "Occupancy detected", "impact": "Lights activated"},
        {"event": "CO2 levels high", "impact": "Ventilation increased"}
    ]
    
    for i, template in enumerate(event_templates[:4]):
        time_point = now - timedelta(minutes=(i+1)*45)
        room = rooms[i % len(rooms)]
        
        events.append(RecentEvent(
            time=time_point.strftime("%H:%M"),
            room=room.name,
            event=template["event"],
            impact=template["impact"]
        ))
    
    return events

@router.get("/agent-decisions/{room_id}", response_model=List[AgentDecision])
async def get_agent_decisions(room_id: int, db: Session = Depends(get_db)):
    """Get recent agent decisions for a specific room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    # Query recent decision logs for this room (most recent first)
    logs = db.query(DecisionLog).filter(DecisionLog.room_id == room_id).order_by(DecisionLog.timestamp.desc()).limit(50).all()

    if not logs:
        return []

    decisions = []
    for log in logs:
        # Map agent id to agent name if possible
        agent = db.query(Agent).filter(Agent.id == log.agent_id).first()
        agent_name = agent.name if agent else (log.agent_id or "unknown")

        decisions.append(AgentDecision(
            time=log.timestamp.strftime("%H:%M") if log.timestamp else "",
            agent=agent_name,
            decision=log.decision or "",
            confidence=round((log.comfort_score or 0.0 + log.energy_score or 0.0 + log.reliability_score or 0.0) / 3.0, 2),
            reasoning=log.reasoning or ""
        ))

    return decisions


@router.get("/coordination-rounds/{room_id}")
async def get_coordination_rounds(room_id: int, db: Session = Depends(get_db)):
    """Return latest coordination summary and recent decision logs for a room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Recent logs
    logs = db.query(DecisionLog).filter(DecisionLog.room_id == room_id).order_by(DecisionLog.timestamp.desc()).limit(100).all()

    return {
        "room_id": room_id,
        "room_name": room.name,
        "last_coordinated_at": room.last_coordinated_at.isoformat() if getattr(room, 'last_coordinated_at', None) else None,
        "last_coordination_summary": room.last_coordination_summary,
        "recent_decision_logs": [l.to_dict() for l in logs]
    }

@router.get("/slo-performance/{room_id}")
async def get_slo_performance(room_id: int, db: Session = Depends(get_db)):
    """Get SLO performance data for a specific room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    slos = db.query(SLO).all()
    
    # Generate realistic SLO performance data
    performance_data = []
    
    slo_mapping = {
        "Comfort SLO": {"current": 22.5, "target": 23.0, "score": 0.92},
        "Energy SLO": {"current": 2.8, "target": 3.0, "score": 0.85}, 
        "Air Quality SLO": {"current": 420, "target": 400, "score": 0.78},
        "Reliability SLO": {"current": 99.2, "target": 99.0, "score": 0.96}
    }
    
    for slo in slos:
        slo_name = f"{slo.name} SLO"
        if slo_name in slo_mapping:
            data = slo_mapping[slo_name]
        else:
            # Generate random realistic data
            data = {
                "current": round(random.uniform(18, 26), 1),
                "target": round(random.uniform(20, 25), 1), 
                "score": round(random.uniform(0.7, 0.95), 2)
            }
        
        performance_data.append({
            "id": slo.id,
            "name": slo.name,
            "current_value": data["current"],
            "target_value": data["target"], 
            "performance_score": data["score"],
            "unit": getattr(slo, 'unit', '°C')
        })
    
    return performance_data
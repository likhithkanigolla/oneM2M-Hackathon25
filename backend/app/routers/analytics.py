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
    
    agents = db.query(Agent).all()
    if not agents:
        return []
    
    # Generate realistic agent decisions
    decisions = []
    now = datetime.now()
    
    decision_templates = [
        {"decision": "Prioritize comfort", "reasoning": "Meeting in progress with 8 participants"},
        {"decision": "Reduce energy consumption", "reasoning": "Peak hour pricing detected"},
        {"decision": "Increase ventilation", "reasoning": "CO2 levels approaching threshold"},
        {"decision": "Maintain current settings", "reasoning": "Optimal balance achieved"},
        {"decision": "Activate emergency mode", "reasoning": "Equipment malfunction detected"},
        {"decision": "Switch to eco mode", "reasoning": "Room unoccupied for 30+ minutes"}
    ]
    
    for i, template in enumerate(decision_templates[:6]):
        time_point = now - timedelta(minutes=(i+1)*20)
        agent = agents[i % len(agents)]
        
        decisions.append(AgentDecision(
            time=time_point.strftime("%H:%M"),
            agent=agent.name,
            decision=template["decision"],
            confidence=round(random.uniform(0.75, 0.98), 2),
            reasoning=template["reasoning"]
        ))
    
    return decisions

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
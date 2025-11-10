from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.models.room import Room
from app.models.agent import Agent
from app.models.slo import SLO
from app.models.decision_log import DecisionLog

router = APIRouter()

# Pydantic models for responses
from pydantic import BaseModel

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
        DecisionLog.timestamp >= since
    ).first()
    
    return {
        "room_id": room_id,
        "room_name": room.name,
        "current_gsi": room.gsi,
        "decisions_24h": decisions,
        "avg_comfort_score": float(avg_scores.avg_comfort or 0),
        "avg_energy_score": float(avg_scores.avg_energy or 0),
        "avg_reliability_score": float(avg_scores.avg_reliability or 0),
    }

@router.get("/agent-performance")
async def get_agent_performance(db: Session = Depends(get_db)):
    """Get performance analytics for all agents"""
    # Last 7 days
    since = datetime.utcnow() - timedelta(days=7)
    
    agents = db.query(Agent).all()
    results = []
    
    for agent in agents:
        decisions = db.query(DecisionLog).filter(
            DecisionLog.agent_id == agent.id,
            DecisionLog.timestamp >= since
        ).count()
        
        avg_scores = db.query(
            func.avg(DecisionLog.comfort_score).label('avg_comfort'),
            func.avg(DecisionLog.energy_score).label('avg_energy'),
            func.avg(DecisionLog.reliability_score).label('avg_reliability')
        ).filter(
            DecisionLog.agent_id == agent.id,
            DecisionLog.timestamp >= since
        ).first()
        
        results.append({
            "agent_id": agent.id,
            "agent_name": agent.name,
            "decisions_7d": decisions,
            "active": agent.active,
            "avg_comfort_score": float(avg_scores.avg_comfort or 0),
            "avg_energy_score": float(avg_scores.avg_energy or 0),
            "avg_reliability_score": float(avg_scores.avg_reliability or 0),
        })
    
    return results

@router.get("/system-overview")
async def get_system_overview(db: Session = Depends(get_db)):
    """Get overall system analytics"""
    total_rooms = db.query(Room).count()
    active_agents = db.query(Agent).filter(Agent.active == True).count()
    total_agents = db.query(Agent).count()
    
    # Decisions in last hour
    since = datetime.utcnow() - timedelta(hours=1)
    recent_decisions = db.query(DecisionLog).filter(
        DecisionLog.timestamp >= since
    ).count()
    
    # Average GSI across all rooms
    avg_gsi = db.query(func.avg(Room.gsi)).scalar() or 0
    
    return {
        "total_rooms": total_rooms,
        "active_agents": active_agents,
        "total_agents": total_agents,
        "decisions_last_hour": recent_decisions,
        "average_gsi": float(avg_gsi),
        "timestamp": datetime.utcnow().isoformat()
    }
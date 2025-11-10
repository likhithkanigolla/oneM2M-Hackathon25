from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.decision_log import DecisionLog
from app.models.room import Room
from app.models.agent import Agent

router = APIRouter()

@router.get("/decision-logs")
async def get_decision_logs(
    db: Session = Depends(get_db),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    limit: Optional[int] = Query(100, description="Number of records to return"),
):
    """Get decision logs with optional filtering"""
    query = db.query(DecisionLog)
    
    if room_id:
        query = query.filter(DecisionLog.room_id == room_id)
    if agent_id:
        query = query.filter(DecisionLog.agent_id == agent_id)
    
    return query.order_by(desc(DecisionLog.timestamp)).limit(limit).all()

@router.get("/room-metrics/{room_id}")
async def get_room_metrics(room_id: int, db: Session = Depends(get_db)):
    """Get analytics for a specific room"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Recent decisions (last 24 hours)
    since = datetime.utcnow() - timedelta(hours=24)
    decisions = db.query(DecisionLog).filter(
        DecisionLog.room_id == room_id,
        DecisionLog.timestamp >= since
    ).count()
    
    # Average scores
    avg_scores = db.query(
        func.avg(DecisionLog.comfort_score).label('avg_comfort'),
        func.avg(DecisionLog.energy_score).label('avg_energy'),
        func.avg(DecisionLog.reliability_score).label('avg_reliability')
    ).filter(
        DecisionLog.room_id == room_id,
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
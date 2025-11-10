from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentBase, AgentCreate, AgentUpdate

router = APIRouter()

@router.get("/", response_model=List[AgentBase])
async def get_agents(db: Session = Depends(get_db)):
    """Get all AI agents"""
    return db.query(Agent).all()

@router.get("/{agent_id}", response_model=AgentBase)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get specific agent by ID"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/", response_model=AgentBase)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create new AI agent"""
    # Check if agent already exists
    existing = db.query(Agent).filter(Agent.id == agent.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent with this ID already exists")
    
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.put("/{agent_id}", response_model=AgentBase)
async def update_agent(agent_id: str, agent: AgentUpdate, db: Session = Depends(get_db)):
    """Update AI agent"""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    for field, value in agent.dict(exclude_unset=True).items():
        setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete AI agent"""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(db_agent)
    db.commit()
    return {"message": "Agent deleted successfully"}

@router.patch("/{agent_id}/toggle")
async def toggle_agent(agent_id: str, db: Session = Depends(get_db)):
    """Toggle agent active status"""
    db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_agent.active = not db_agent.active
    db.commit()
    db.refresh(db_agent)
    return db_agent
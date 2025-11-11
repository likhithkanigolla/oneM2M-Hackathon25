"""
Test endpoints for LLM agent integration

This module provides testing endpoints for validating Google Gemini API integration
and agent decision-making capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from ..database import get_db
from ..models.room import Room
from ..services.decision_engine import MultiAgentDecisionEngine
from ..agents.gemini_client import is_gemini_available, get_gemini_client
import os

router = APIRouter(prefix="/api/llm", tags=["LLM Testing"])

@router.get("/status")
async def get_llm_status():
    """Get current LLM integration status"""
    return {
        "gemini_available": is_gemini_available(),
        "api_key_configured": bool(os.getenv('GOOGLE_API_KEY')),
        "client_initialized": get_gemini_client() is not None
    }

@router.post("/test-decision/{room_id}")
async def test_room_decision(
    room_id: int,
    context: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Test LLM decision making for a specific room"""
    
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    try:
        # Initialize decision engine
        engine = MultiAgentDecisionEngine(db)
        
        # Make decision
        decision = await engine.make_room_decision(room_id, context)
        
        return {
            "room_id": room_id,
            "room_name": room.name,
            "decision": decision.__dict__ if hasattr(decision, '__dict__') else decision,
            "llm_enabled": is_gemini_available(),
            "timestamp": decision.timestamp if hasattr(decision, 'timestamp') else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision making failed: {str(e)}")

@router.post("/test-gemini")
async def test_gemini_direct():
    """Direct test of Gemini API integration"""
    
    if not is_gemini_available():
        raise HTTPException(
            status_code=503, 
            detail="Gemini API not available. Check GOOGLE_API_KEY environment variable."
        )
    
    try:
        client = get_gemini_client()
        
        # Test prompt
        test_prompt = """
You are a test agent. Respond with a simple JSON decision for turning on lights in a room.
"""
        
        test_context = {
            "room_data": {"id": 1, "name": "Test Room"},
            "devices": [
                {"id": "light_1", "type": "Lighting", "status": "OFF", "name": "Main Light"}
            ],
            "sensor_data": {"occupancy": 2, "temperature": 22},
            "slos": []
        }
        
        response = await client.generate_decision(test_prompt, test_context)
        
        return {
            "test_successful": True,
            "response": response,
            "api_working": True
        }
        
    except Exception as e:
        return {
            "test_successful": False,
            "error": str(e),
            "api_working": False
        }

@router.get("/agent-types")
async def get_available_agents():
    """Get list of available LLM agent types"""
    from ..agents.agent_config import AgentType, AgentRegistry
    
    agents = []
    for agent_type in AgentType:
        config = AgentRegistry.get_agent_config(agent_type)
        agents.append({
            "type": agent_type.value,
            "priority": config.priority_weight,
            "goal": config.goal,
            "constraints": config.constraints
        })
    
    return {
        "available_agents": agents,
        "total_count": len(agents)
    }
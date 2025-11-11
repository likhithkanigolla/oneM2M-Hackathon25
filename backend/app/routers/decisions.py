"""
Decision Management API Routes

This module provides API endpoints for coordinating agent decisions,
executing plans, and managing SLO compliance.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db

# Import decision management services
from ..services.decision_coordinator import MultiAgentCoordinator
from ..services.execution_engine import DecisionExecutionEngine  
from ..services.slo_service import SLOService

# Import models
from ..models.slo import SLO
from ..models.room import Room
from ..models.device import Device

router = APIRouter()

# Note: Services that require DB sessions will be instantiated within endpoints
# Global instances only for stateless services
coordinator = MultiAgentCoordinator()
execution_engine = DecisionExecutionEngine()
slo_service = SLOService()


@router.post("/coordinate")
async def coordinate_decisions(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Coordinate decisions from all agents and generate ranked decision plans
    
    This endpoint:
    1. Gathers current room and sensor data
    2. Calls all 6 LLM agents to get decisions
    3. Resolves conflicts using different strategies
    4. Scores plans against SLO compliance
    5. Returns ranked decision plans
    """
    
    try:
        room_id = request.get('room_id', 1)
        
        # Get room data
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get devices for the room
        devices = db.query(Device).filter(Device.room_id == room_id).all()
        device_data = [device.to_dict() for device in devices]
        
        # Get mock sensor data (in production, use real sensor service)
        sensor_data = {
            'temperature': 22.5,
            'humidity': 45,
            'co2': 400,
            'occupancy': 0,
            'light_level': 300,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get active SLOs
        slos = db.query(SLO).filter(SLO.active == True).all()
        
        # Build context for agents
        context = {
            'room_data': room.to_dict(),
            'devices': device_data,
            'sensor_data': sensor_data,
            'slos': [slo.to_dict() for slo in slos],
            'timestamp': datetime.now().isoformat()
        }
        
        # Coordinate decisions
        resolution_strategies = request.get('resolution_strategies', ['priority_weighted', 'safety_first'])
        decision_plans = await coordinator.coordinate_decisions(context, slos, resolution_strategies)
        
        # Get execution summary
        execution_summary = coordinator.get_execution_summary(decision_plans)
        
        # Format response
        return {
            'room_id': room_id,
            'total_plans': len(decision_plans),
            'plans': [plan.to_dict() for plan in decision_plans],
            'execution_summary': execution_summary,
            'coordination_time': datetime.now().isoformat(),
            'context_summary': {
                'devices_count': len(device_data),
                'active_slos': len(slos),
                'sensor_data_timestamp': sensor_data.get('timestamp'),
                'occupancy': sensor_data.get('occupancy', 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision coordination failed: {str(e)}")


@router.post("/execute")
async def execute_decision_plan(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute a decision plan
    """
    
    try:
        # Validate plan exists
        plan_data = request.get('plan_data')
        if not plan_data:
            raise HTTPException(status_code=400, detail="Plan data required")
        
        # Create decision plan object
        from ..services.decision_coordinator import DecisionPlan
        decision_plan = DecisionPlan(
            plan_id=plan_data.get('plan_id', f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            agent_decisions=plan_data.get('agent_decisions', []),
            slo_compliance=plan_data.get('slo_compliance', {}),
            metadata=plan_data.get('metadata', {})
        )
        decision_plan.actions = plan_data.get('actions', [])
        decision_plan.score = plan_data.get('score', 0.0)
        decision_plan.confidence = plan_data.get('confidence', 0.0)
        
        # Execute plan
        execution_mode = request.get('execution_mode', 'MANUAL').upper()
        executor = request.get('executor', 'system')
        
        execution_plan = await execution_engine.execute_plan(
            decision_plan, 
            execution_mode=execution_mode, 
            executor=executor
        )
        
        return {
            'plan_id': execution_plan.plan_id,
            'status': execution_plan.status.value,
            'execution_mode': execution_plan.execution_mode,
            'approval_required': execution_plan.approval_required,
            'approved': execution_plan.approved,
            'progress_percentage': execution_plan.get_progress_percentage(),
            'execution_details': execution_plan.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan execution failed: {str(e)}")


@router.get("/status/{plan_id}")
async def get_execution_status(plan_id: str):
    """Get the execution status of a decision plan"""
    
    try:
        execution_data = execution_engine.get_execution_status(plan_id)
        
        if not execution_data:
            raise HTTPException(status_code=404, detail="Execution plan not found")
        
        return {
            'plan_id': plan_id,
            'status': execution_data.get('status'),
            'execution_mode': execution_data.get('execution_mode'),
            'approval_required': execution_data.get('approval_required'),
            'approved': execution_data.get('approved'),
            'progress_percentage': execution_data.get('completed_actions', 0) / max(execution_data.get('total_actions', 1), 1) * 100,
            'execution_details': execution_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.post("/slos/evaluate/{room_id}")
async def evaluate_slos(
    room_id: int,
    db: Session = Depends(get_db)
):
    """
    Evaluate current room state against all active SLOs
    """
    
    try:
        # Get room data
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get devices and mock sensor data
        devices = db.query(Device).filter(Device.room_id == room_id).all()
        device_data = [device.to_dict() for device in devices]
        
        sensor_data = {
            'temperature': 25.0,  # Slightly high temperature
            'humidity': 60,
            'co2': 450,
            'occupancy': 2,
            'light_level': 400,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get active SLOs
        slos = db.query(SLO).filter(SLO.active == True).all()
        
        # Evaluate SLOs
        evaluation_results = slo_service.evaluate_slos(
            room_data=room.to_dict(),
            sensor_data=sensor_data,
            devices=device_data,
            slos=slos
        )
        
        # Get compliance summary
        compliance_summary = slo_service.get_compliance_summary(evaluation_results)
        
        return {
            'room_id': room_id,
            'overall_compliance': evaluation_results.get('overall_compliance', 0.0),
            'category_scores': evaluation_results.get('scores', {}),
            'violations': evaluation_results.get('violations', []),
            'slo_results': evaluation_results.get('slo_results', []),
            'recommendations': evaluation_results.get('recommendations', []),
            'compliance_summary': compliance_summary,
            'evaluation_time': evaluation_results.get('evaluation_time')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SLO evaluation failed: {str(e)}")


@router.post("/slos/initialize")
async def initialize_default_slos(db: Session = Depends(get_db)):
    """Initialize the system with default smart building SLOs"""
    
    try:
        # Check if SLOs already exist
        existing_slos = db.query(SLO).filter(SLO.is_system_defined == True).count()
        
        if existing_slos > 0:
            return {
                "message": f"Default SLOs already exist ({existing_slos} found)",
                "existing_slos": existing_slos
            }
        
        # Create default SLOs
        created_slos = slo_service.create_default_slos(db, created_by="system")
        
        return {
            "message": "Default SLOs created successfully",
            "created_slos": len(created_slos),
            "slos": [slo.to_dict() for slo in created_slos]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SLO initialization failed: {str(e)}")


@router.get("/execution-summary")
async def get_execution_summary():
    """Get a summary of all execution activity"""
    
    try:
        summary = execution_engine.get_execution_summary()
        
        return {
            "execution_summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get execution summary: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the decision management system"""
    
    try:
        # Check if all services are operational
        health_status = {
            "decision_coordinator": "operational",
            "execution_engine": "operational",
            "slo_service": "operational",
            "llm_integration": "checking..."
        }
        
        # Quick LLM availability check
        from ..agents.gemini_client import is_gemini_available
        health_status["llm_integration"] = "operational" if is_gemini_available() else "degraded"
        
        return {
            "status": "healthy",
            "services": health_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/approve/{plan_id}")
async def approve_execution_plan(
    plan_id: str,
    request: Dict[str, str],
    background_tasks: BackgroundTasks
):
    """Approve and execute a pending plan"""
    
    try:
        approved_by = request.get('approved_by', 'system')
        execution_plan = await execution_engine.approve_and_execute_plan(plan_id, approved_by)
        
        if not execution_plan:
            raise HTTPException(status_code=404, detail="Plan not found or not pending approval")
        
        return {
            "message": "Plan approved and execution started",
            "plan_id": plan_id,
            "approved_by": approved_by,
            "status": execution_plan.status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")


@router.get("/pending-approvals")
async def get_pending_approvals():
    """Get all execution plans pending approval"""
    
    try:
        pending = execution_engine.get_pending_approvals()
        
        return {
            "pending_approvals": len(pending),
            "plans": pending
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending approvals: {str(e)}")


@router.delete("/cancel/{plan_id}")
async def cancel_execution(plan_id: str, request: Dict[str, str] = None):
    """Cancel a pending or in-progress execution"""
    
    try:
        cancelled_by = request.get('cancelled_by', 'system') if request else 'system'
        success = execution_engine.cancel_execution(plan_id, cancelled_by)
        
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found or cannot be cancelled")
        
        return {
            "message": "Execution cancelled successfully",
            "plan_id": plan_id,
            "cancelled_by": cancelled_by
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cancellation failed: {str(e)}")


@router.post("/slos/initialize")
async def initialize_default_slos(db: Session = Depends(get_db)):
    """Initialize the system with default smart building SLOs"""
    
    try:
        # Check if SLOs already exist
        existing_slos = db.query(SLO).filter(SLO.is_system_defined == True).count()
        
        if existing_slos > 0:
            return {
                "message": f"Default SLOs already exist ({existing_slos} found)",
                "existing_slos": existing_slos
            }
        
        # Create default SLOs
        created_slos = slo_service.create_default_slos(db, created_by="system")
        
        return {
            "message": "Default SLOs created successfully",
            "created_slos": len(created_slos),
            "slos": [slo.to_dict() for slo in created_slos]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SLO initialization failed: {str(e)}")


@router.get("/execution-summary")
async def get_execution_summary():
    """Get a summary of all execution activity"""
    
    try:
        summary = execution_engine.get_execution_summary()
        
        return {
            "execution_summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get execution summary: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the decision management system"""
    
    try:
        # Check if all services are operational
        health_status = {
            "decision_coordinator": "operational",
            "execution_engine": "operational",
            "slo_service": "operational",
            "llm_integration": "checking..."
        }
        
        # Quick LLM availability check
        from ..agents.gemini_client import is_gemini_available
        health_status["llm_integration"] = "operational" if is_gemini_available() else "degraded"
        
        return {
            "status": "healthy",
            "services": health_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
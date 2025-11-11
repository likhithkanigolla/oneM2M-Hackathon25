"""
Decision Management Schemas

Pydantic schemas for decision coordination, execution, and SLO evaluation
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DecisionCoordinationRequest(BaseModel):
    """Request for coordinating agent decisions"""
    room_id: int = Field(..., description="ID of the room to coordinate decisions for")
    resolution_strategies: Optional[List[str]] = Field(
        default=['priority_weighted', 'safety_first', 'energy_balance'],
        description="List of conflict resolution strategies to use"
    )
    context_override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context data to override current room state"
    )


class DecisionCoordinationResponse(BaseModel):
    """Response containing ranked decision plans"""
    room_id: int
    total_plans: int
    plans: List[Dict[str, Any]]
    execution_summary: Dict[str, Any]
    coordination_time: str
    context_summary: Dict[str, Any]


class ExecutionRequest(BaseModel):
    """Request to execute a decision plan"""
    plan_data: Dict[str, Any] = Field(..., description="The decision plan to execute")
    execution_mode: str = Field(
        default="MANUAL",
        description="Execution mode: AUTO, MANUAL, or REVIEW"
    )
    executor: Optional[str] = Field(
        default=None,
        description="Username of the person executing the plan"
    )


class ExecutionStatusResponse(BaseModel):
    """Response containing execution status"""
    plan_id: str
    status: str
    execution_mode: str
    approval_required: bool
    approved: bool
    progress_percentage: float
    execution_details: Dict[str, Any]


class SLOEvaluationResponse(BaseModel):
    """Response containing SLO evaluation results"""
    room_id: int
    overall_compliance: float
    category_scores: Dict[str, float]
    violations: List[Dict[str, Any]]
    slo_results: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_summary: Dict[str, Any]
    evaluation_time: Optional[str]


class ApprovalRequest(BaseModel):
    """Request to approve an execution plan"""
    approved_by: str = Field(..., description="Username of the approver")
    approval_notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the approval"
    )


class DeviceActionSchema(BaseModel):
    """Schema for a single device action"""
    device_id: str
    action: str
    parameters: Optional[Dict[str, Any]] = {}
    priority: Optional[float] = 0.5
    reason: Optional[str] = None


class AgentDecisionSchema(BaseModel):
    """Schema for an agent's decision"""
    agent_id: str
    agent_type: str
    priority: float
    timestamp: str
    decisions: List[DeviceActionSchema]
    reasoning: str
    scores: Dict[str, float]
    confidence: Optional[float] = 0.5


class DecisionPlanSchema(BaseModel):
    """Schema for a complete decision plan"""
    plan_id: str
    score: float
    confidence: float
    slo_compliance: Dict[str, Any]
    actions: List[DeviceActionSchema]
    reasoning: str
    agent_decisions: List[AgentDecisionSchema]
    metadata: Dict[str, Any]
    timestamp: str


class ExecutionResultSchema(BaseModel):
    """Schema for execution results"""
    action: DeviceActionSchema
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    execution_time_ms: Optional[float]
    error_message: Optional[str]
    response_data: Optional[Dict[str, Any]]


class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    status: str
    services: Dict[str, str]
    timestamp: str
    error: Optional[str] = None


class SLOViolationSchema(BaseModel):
    """Schema for SLO violations"""
    slo_name: str
    expected: str
    actual: str
    severity: str
    recommendation: str


class ComplianceSummarySchema(BaseModel):
    """Schema for compliance summary"""
    overall_compliance: float
    category_scores: Dict[str, float]
    total_slos: int
    violations: int
    recommendations: int
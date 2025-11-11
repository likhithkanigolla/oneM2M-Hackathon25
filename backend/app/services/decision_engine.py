"""
Multi-Agent Decision Engine

This engine orchestrates multiple LLM agents to make collective decisions
about smart room control, handling conflicts and priorities.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from sqlalchemy.orm import Session

from app.agents.llm_agents import SecurityAgent, ComfortAgent, EnergyAgent
from app.agents.agent_config import AgentType, AgentRegistry
from app.services.sensor_service import SensorDataService
from app.models.device import Device
from app.models.slo import SLO
from app.models.room import Room
from app.models.decision_log import DecisionLog

class DecisionStatus(Enum):
    CONSENSUS = "consensus"
    MAJORITY = "majority"  
    CONFLICT = "conflict"
    MANUAL_REVIEW = "manual_review"
    EMERGENCY_OVERRIDE = "emergency_override"

class ConflictResolution(Enum):
    PRIORITY_WEIGHTED = "priority_weighted"
    MAJORITY_VOTE = "majority_vote"
    SAFETY_FIRST = "safety_first"
    MANUAL_ESCALATION = "manual_escalation"

@dataclass
class AgentDecision:
    """Individual agent decision"""
    agent_id: str
    agent_type: str
    priority: float
    decisions: List[Dict[str, Any]]
    reasoning: str
    scores: Dict[str, float]
    timestamp: str
    confidence: float = 0.8

@dataclass
class CollectiveDecision:
    """Final collective decision from all agents"""
    room_id: int
    timestamp: str
    status: DecisionStatus
    final_actions: List[Dict[str, Any]]
    agent_decisions: List[AgentDecision]
    conflict_resolution: Optional[ConflictResolution]
    reasoning: str
    confidence: float
    requires_manual_review: bool
    emergency_level: int = 0  # 0-10 scale

class MultiAgentDecisionEngine:
    """
    Orchestrates multiple LLM agents for smart room decision making
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.sensor_service = SensorDataService(db)
        self.agents = self._initialize_agents()
        self.conflict_resolution_strategy = ConflictResolution.PRIORITY_WEIGHTED
        
    def _initialize_agents(self) -> Dict[AgentType, Any]:
        """Initialize all available agents"""
        return {
            AgentType.SECURITY: SecurityAgent(),
            AgentType.COMFORT: ComfortAgent(),
            AgentType.ENERGY_EFFICIENCY: EnergyAgent(),
            # Add more agents as they're implemented
        }

    async def make_room_decision(self, room_id: int, context: Dict[str, Any] = None) -> CollectiveDecision:
        """
        Orchestrate decision making for a specific room
        
        Args:
            room_id: Room identifier
            context: Additional context for decision making
            
        Returns:
            CollectiveDecision with final actions and reasoning
        """
        # Gather all necessary data
        decision_context = await self._gather_decision_context(room_id, context)
        
        # Get decisions from all active agents
        agent_decisions = await self._collect_agent_decisions(decision_context)
        
        # Resolve conflicts and make final decision
        collective_decision = await self._resolve_conflicts(room_id, agent_decisions)
        
        # Log decision for audit trail
        await self._log_decision(collective_decision)
        
        return collective_decision

    async def _gather_decision_context(self, room_id: int, additional_context: Dict = None) -> Dict[str, Any]:
        """Gather all data needed for agent decision making"""
        
        # Get room information
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise ValueError(f"Room {room_id} not found")
        
        # Get devices in the room
        devices = self.db.query(Device).filter(Device.room_id == room_id).all()
        device_data = [device.to_dict() for device in devices]
        
        # Get SLOs that apply to this room
        slos = self.db.query(SLO).filter(SLO.active == True).all()
        slo_data = [slo.to_dict() for slo in slos]
        
        # Get sensor data (use mock data for now)
        sensor_data = self.sensor_service.create_mock_sensor_data(room_id)
        
        # Get recent decision history
        recent_decisions = self.db.query(DecisionLog).filter(
            DecisionLog.room_id == room_id
        ).order_by(DecisionLog.timestamp.desc()).limit(5).all()
        
        context = {
            "room_data": room.to_dict(),
            "devices": device_data,
            "slos": slo_data,
            "sensor_data": sensor_data,
            "recent_decisions": [d.to_dict() for d in recent_decisions],
            "timestamp": datetime.now().isoformat(),
            "decision_id": f"decision_{room_id}_{int(datetime.now().timestamp())}"
        }
        
        if additional_context:
            context.update(additional_context)
            
        return context

    async def _collect_agent_decisions(self, context: Dict[str, Any]) -> List[AgentDecision]:
        """Collect decisions from all active agents"""
        
        agent_decisions = []
        
        # Run agents in parallel for efficiency
        tasks = []
        for agent_type, agent in self.agents.items():
            if agent.is_active():
                task = asyncio.create_task(agent.make_decision(context))
                tasks.append((agent_type, task))
        
        # Wait for all agents to complete
        for agent_type, task in tasks:
            try:
                decision_data = await task
                
                agent_decision = AgentDecision(
                    agent_id=decision_data.get("agent_id", str(agent_type.value)),
                    agent_type=decision_data.get("agent_type", agent_type.value),
                    priority=decision_data.get("priority", 0.5),
                    decisions=decision_data.get("decisions", []),
                    reasoning=decision_data.get("reasoning", ""),
                    scores=decision_data.get("scores", {}),
                    timestamp=decision_data.get("timestamp", datetime.now().isoformat()),
                    confidence=decision_data.get("confidence", 0.8)
                )
                
                agent_decisions.append(agent_decision)
                
            except Exception as e:
                print(f"Error getting decision from {agent_type}: {e}")
                # Continue with other agents
                
        return agent_decisions

    async def _resolve_conflicts(self, room_id: int, agent_decisions: List[AgentDecision]) -> CollectiveDecision:
        """
        Resolve conflicts between agent decisions and create final decision
        """
        if not agent_decisions:
            return CollectiveDecision(
                room_id=room_id,
                timestamp=datetime.now().isoformat(),
                status=DecisionStatus.MANUAL_REVIEW,
                final_actions=[],
                agent_decisions=[],
                conflict_resolution=None,
                reasoning="No agent decisions available",
                confidence=0.0,
                requires_manual_review=True
            )
        
        # Aggregate all proposed device actions
        device_actions = self._aggregate_device_actions(agent_decisions)
        
        # Check for conflicts
        conflicts = self._detect_conflicts(device_actions)
        
        if not conflicts:
            # No conflicts - consensus or compatible actions
            status = DecisionStatus.CONSENSUS
            final_actions = self._merge_compatible_actions(device_actions)
            conflict_resolution = None
            reasoning = "All agents agree or have compatible recommendations"
            requires_manual_review = False
            
        elif self.conflict_resolution_strategy == ConflictResolution.PRIORITY_WEIGHTED:
            # Resolve using agent priority weights
            status, final_actions, reasoning = self._resolve_by_priority(device_actions, agent_decisions)
            conflict_resolution = ConflictResolution.PRIORITY_WEIGHTED
            requires_manual_review = status == DecisionStatus.MANUAL_REVIEW
            
        elif self.conflict_resolution_strategy == ConflictResolution.MAJORITY_VOTE:
            # Resolve using majority voting
            status, final_actions, reasoning = self._resolve_by_majority(device_actions, agent_decisions)
            conflict_resolution = ConflictResolution.MAJORITY_VOTE
            requires_manual_review = status == DecisionStatus.MANUAL_REVIEW
            
        else:
            # Escalate to manual review
            status = DecisionStatus.MANUAL_REVIEW
            final_actions = []
            conflict_resolution = ConflictResolution.MANUAL_ESCALATION
            reasoning = "Conflicts detected, escalating to manual review"
            requires_manual_review = True
        
        # Calculate overall confidence
        confidence = sum(d.confidence * d.priority for d in agent_decisions) / sum(d.priority for d in agent_decisions)
        
        return CollectiveDecision(
            room_id=room_id,
            timestamp=datetime.now().isoformat(),
            status=status,
            final_actions=final_actions,
            agent_decisions=agent_decisions,
            conflict_resolution=conflict_resolution,
            reasoning=reasoning,
            confidence=confidence,
            requires_manual_review=requires_manual_review
        )

    def _aggregate_device_actions(self, agent_decisions: List[AgentDecision]) -> Dict[str, List[Dict[str, Any]]]:
        """Group all proposed actions by device ID"""
        device_actions = {}
        
        for decision in agent_decisions:
            for action in decision.decisions:
                device_id = action.get("device_id")
                if device_id:
                    if device_id not in device_actions:
                        device_actions[device_id] = []
                    
                    action_with_agent = action.copy()
                    action_with_agent["agent_id"] = decision.agent_id
                    action_with_agent["agent_type"] = decision.agent_type
                    action_with_agent["priority"] = decision.priority
                    device_actions[device_id].append(action_with_agent)
        
        return device_actions

    def _detect_conflicts(self, device_actions: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Detect conflicting actions for the same device"""
        conflicts = []
        
        for device_id, actions in device_actions.items():
            if len(actions) > 1:
                # Check if actions are conflicting
                action_types = [action.get("action") for action in actions]
                unique_actions = set(action_types)
                
                # Conflict if different actions proposed for same device
                if len(unique_actions) > 1:
                    # Check for specific conflicts
                    if "turn_on" in unique_actions and "turn_off" in unique_actions:
                        conflicts.append(f"Device {device_id}: On/Off conflict")
                    elif len(unique_actions) > 1:
                        conflicts.append(f"Device {device_id}: Multiple different actions")
        
        return conflicts

    def _merge_compatible_actions(self, device_actions: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge compatible actions into final action list"""
        final_actions = []
        
        for device_id, actions in device_actions.items():
            if len(actions) == 1:
                # Single action - use as is
                final_actions.append(actions[0])
            else:
                # Multiple compatible actions - use highest priority
                highest_priority_action = max(actions, key=lambda x: x.get("priority", 0))
                final_actions.append(highest_priority_action)
        
        return final_actions

    def _resolve_by_priority(self, device_actions: Dict[str, List[Dict[str, Any]]], 
                           agent_decisions: List[AgentDecision]) -> Tuple[DecisionStatus, List[Dict[str, Any]], str]:
        """Resolve conflicts using agent priority weights"""
        final_actions = []
        reasoning_parts = []
        
        for device_id, actions in device_actions.items():
            if len(actions) == 1:
                final_actions.append(actions[0])
                continue
            
            # Find highest priority action for this device
            highest_priority_action = max(actions, key=lambda x: x.get("priority", 0))
            final_actions.append(highest_priority_action)
            
            if len(actions) > 1:
                reasoning_parts.append(
                    f"Device {device_id}: Chose {highest_priority_action['agent_type']} "
                    f"recommendation (priority {highest_priority_action['priority']}) "
                    f"over {len(actions)-1} other(s)"
                )
        
        reasoning = "Priority-weighted resolution: " + "; ".join(reasoning_parts) if reasoning_parts else "No conflicts to resolve"
        
        # Check if any critical conflicts remain
        emergency_agents = [d for d in agent_decisions if d.agent_type in ["emergency", "security"]]
        if emergency_agents:
            return DecisionStatus.EMERGENCY_OVERRIDE, final_actions, f"Emergency override: {reasoning}"
        
        return DecisionStatus.MAJORITY, final_actions, reasoning

    def _resolve_by_majority(self, device_actions: Dict[str, List[Dict[str, Any]]], 
                           agent_decisions: List[AgentDecision]) -> Tuple[DecisionStatus, List[Dict[str, Any]], str]:
        """Resolve conflicts using majority voting"""
        final_actions = []
        reasoning_parts = []
        
        for device_id, actions in device_actions.items():
            if len(actions) == 1:
                final_actions.append(actions[0])
                continue
            
            # Count votes for each action type
            action_votes = {}
            for action in actions:
                action_type = action.get("action")
                if action_type not in action_votes:
                    action_votes[action_type] = []
                action_votes[action_type].append(action)
            
            # Find majority action
            max_votes = max(len(votes) for votes in action_votes.values())
            majority_actions = [action_type for action_type, votes in action_votes.items() if len(votes) == max_votes]
            
            if len(majority_actions) == 1:
                # Clear majority
                majority_action_type = majority_actions[0]
                chosen_action = action_votes[majority_action_type][0]  # Take first of majority
                final_actions.append(chosen_action)
                reasoning_parts.append(f"Device {device_id}: Majority vote for {majority_action_type}")
            else:
                # Tie - escalate to manual review
                return DecisionStatus.MANUAL_REVIEW, [], f"Tie vote for device {device_id}, manual review required"
        
        reasoning = "Majority vote resolution: " + "; ".join(reasoning_parts) if reasoning_parts else "No conflicts to resolve"
        return DecisionStatus.MAJORITY, final_actions, reasoning

    async def _log_decision(self, decision: CollectiveDecision):
        """Log decision for audit trail"""
        try:
            decision_log = DecisionLog(
                room_id=decision.room_id,
                decision_data=asdict(decision),
                status=decision.status.value,
                confidence_score=decision.confidence,
                manual_review_required=decision.requires_manual_review
            )
            
            self.db.add(decision_log)
            self.db.commit()
        except Exception as e:
            print(f"Error logging decision: {e}")

    def set_conflict_resolution_strategy(self, strategy: ConflictResolution):
        """Update conflict resolution strategy"""
        self.conflict_resolution_strategy = strategy

    def get_decision_history(self, room_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent decision history for a room"""
        decisions = self.db.query(DecisionLog).filter(
            DecisionLog.room_id == room_id
        ).order_by(DecisionLog.timestamp.desc()).limit(limit).all()
        
        return [decision.to_dict() for decision in decisions]

# Legacy compatibility class
class DecisionEngine(MultiAgentDecisionEngine):
    """Legacy wrapper for backwards compatibility"""
    
    def __init__(self, db: Session = None):
        if db:
            super().__init__(db)
        else:
            # Fallback to basic implementation for compatibility
            self.agents = {"base": type('BaseAgent', (), {'is_active': lambda: True, 'make_decision': lambda ctx: {"action": "noop"}})}

    async def get_agent_decisions(self, room, slos, active_scenarios) -> Dict:
        """Legacy method for compatibility"""
        if hasattr(self, 'db'):
            # Use new system
            context = self._build_context(room, slos, active_scenarios)
            agent_decisions = await self._collect_agent_decisions(context)
            return {d.agent_id: asdict(d) for d in agent_decisions}
        else:
            # Legacy fallback
            context = self._build_context(room, slos, active_scenarios)
            decisions = {}
            for agent_id, agent in self.agents.items():
                if agent.is_active():
                    decision = await agent.make_decision(context)
                    decisions[agent_id] = decision
            return decisions

    def _build_context(self, room, slos, scenarios):
        return {
            "room_state": getattr(room, "to_dict", lambda: room)(),
            "slos": slos,
            "active_scenarios": [s for s in (scenarios or [])],
        }

    async def aggregate_decision(self, decisions: Dict, agent_weights: Dict) -> str:
        """Legacy aggregation method"""
        return "aggregate_placeholder"

"""
Multi-Agent Decision Coordinator

This module coordinates decisions from all smart building agents,
resolves conflicts, and generates ranked decision plans.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

from ..agents.llm_agents import (
    SecurityAgent, ComfortAgent, EnergyAgent, 
    EmergencyAgent, EnvironmentalAgent, OccupancyAgent
)
from .slo_service import SLOService
from ..agents.agent_config import AgentType
from ..models.slo import SLO


class DecisionPlan:
    """Represents a decision plan with actions and scoring"""
    
    def __init__(self, plan_id: str, agent_decisions: List[Dict[str, Any]], 
                 slo_compliance: Dict[str, Any], metadata: Dict[str, Any] = None):
        self.plan_id = plan_id
        self.agent_decisions = agent_decisions
        self.slo_compliance = slo_compliance
        self.metadata = metadata or {}
        self.score = 0.0
        self.confidence = 0.0
        self.actions = []
        self.reasoning = ""
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_id': self.plan_id,
            'score': self.score,
            'confidence': self.confidence,
            'slo_compliance': self.slo_compliance,
            'actions': self.actions,
            'reasoning': self.reasoning,
            'agent_decisions': self.agent_decisions,
            'metadata': self.metadata,
            'timestamp': datetime.now().isoformat()
        }


class ConflictResolver:
    """Resolves conflicts between agent decisions"""
    
    def __init__(self):
        self.resolution_strategies = {
            'priority_weighted': self._priority_weighted_resolution,
            'majority_vote': self._majority_vote_resolution, 
            'safety_first': self._safety_first_resolution,
            'energy_balance': self._energy_balance_resolution
        }
    
    def resolve_conflicts(self, agent_decisions: List[Dict[str, Any]], 
                         strategy: str = 'priority_weighted') -> Dict[str, Any]:
        """Resolve conflicts between agent decisions"""
        
        if strategy in self.resolution_strategies:
            return self.resolution_strategies[strategy](agent_decisions)
        else:
            return self._priority_weighted_resolution(agent_decisions)
    
    def _priority_weighted_resolution(self, agent_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts using agent priority weights"""
        
        # Group decisions by device
        device_decisions = {}
        for decision in agent_decisions:
            agent_priority = decision.get('priority', 0.5)
            for action in decision.get('decisions', []):
                device_id = action.get('device_id')
                if device_id not in device_decisions:
                    device_decisions[device_id] = []
                device_decisions[device_id].append({
                    'action': action,
                    'agent': decision.get('agent_type'),
                    'priority': agent_priority,
                    'reasoning': decision.get('reasoning', '')
                })
        
        # Resolve conflicts for each device
        resolved_actions = []
        conflict_info = []
        
        for device_id, conflicts in device_decisions.items():
            if len(conflicts) == 1:
                # No conflict
                resolved_actions.append(conflicts[0]['action'])
            else:
                # Multiple agents want to control same device
                # Choose highest priority agent
                winner = max(conflicts, key=lambda x: x['priority'])
                resolved_actions.append(winner['action'])
                
                conflict_info.append({
                    'device_id': device_id,
                    'conflicting_agents': [c['agent'] for c in conflicts],
                    'winner': winner['agent'],
                    'resolution_method': 'priority_weighted'
                })
        
        return {
            'resolved_actions': resolved_actions,
            'conflicts': conflict_info,
            'resolution_method': 'priority_weighted'
        }
    
    def _majority_vote_resolution(self, agent_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts using majority voting"""
        
        action_votes = {}
        for decision in agent_decisions:
            for action in decision.get('decisions', []):
                device_id = action.get('device_id')
                action_type = action.get('action')
                key = f"{device_id}_{action_type}"
                
                if key not in action_votes:
                    action_votes[key] = {'action': action, 'votes': 0, 'voters': []}
                action_votes[key]['votes'] += 1
                action_votes[key]['voters'].append(decision.get('agent_type'))
        
        # Choose actions with most votes
        resolved_actions = []
        for key, vote_data in action_votes.items():
            if vote_data['votes'] >= 2:  # Majority threshold
                resolved_actions.append(vote_data['action'])
        
        return {
            'resolved_actions': resolved_actions,
            'conflicts': [],
            'resolution_method': 'majority_vote'
        }
    
    def _safety_first_resolution(self, agent_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prioritize safety and emergency decisions"""
        # Priority order: Emergency > Security > Environmental > Comfort > Occupancy > Energy
        priority_order = [
            AgentType.EMERGENCY_RESPONSE.value,
            AgentType.SECURITY.value,
            AgentType.ENVIRONMENTAL.value,
            AgentType.COMFORT.value,
            AgentType.OCCUPANCY.value,
            AgentType.ENERGY_EFFICIENCY.value,
        ]

        # Sort decisions by safety priority. If agent_type not found, treat as low priority.
        def _priority_key(x):
            atype = x.get('agent_type')
            try:
                return priority_order.index(atype)
            except ValueError:
                return len(priority_order)

        sorted_decisions = sorted(agent_decisions, key=_priority_key)
        
        device_assignments = {}
        resolved_actions = []
        
        for decision in sorted_decisions:
            for action in decision.get('decisions', []):
                device_id = action.get('device_id')
                if device_id not in device_assignments:
                    device_assignments[device_id] = decision.get('agent_type')
                    resolved_actions.append(action)
        
        return {
            'resolved_actions': resolved_actions,
            'conflicts': [],
            'resolution_method': 'safety_first'
        }
    
    def _energy_balance_resolution(self, agent_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Balance energy efficiency with other needs"""
        
        energy_decisions = []
        other_decisions = []
        
        for decision in agent_decisions:
            if decision.get('agent_type') == 'ENERGY_EFFICIENCY':
                energy_decisions.extend(decision.get('decisions', []))
            else:
                other_decisions.extend(decision.get('decisions', []))
        
        # Prefer non-energy decisions but consider energy constraints
        resolved_actions = other_decisions.copy()
        
        # Add energy decisions that don't conflict
        used_devices = {action.get('device_id') for action in other_decisions}
        for energy_action in energy_decisions:
            if energy_action.get('device_id') not in used_devices:
                resolved_actions.append(energy_action)
        
        return {
            'resolved_actions': resolved_actions,
            'conflicts': [],
            'resolution_method': 'energy_balance'
        }


class DecisionPlanScorer:
    """Scores decision plans based on SLO compliance and impact"""
    
    def __init__(self):
        self.slo_service = SLOService()
    
    def score_decision_plan(self, plan: DecisionPlan, current_state: Dict[str, Any], 
                           slos: List[SLO]) -> float:
        """Score a decision plan based on expected outcomes"""
        
        # Simulate the impact of the decision plan
        predicted_state = self._simulate_plan_impact(plan, current_state)
        
        # Evaluate SLO compliance after plan execution
        predicted_evaluation = self.slo_service.evaluate_slos(
            predicted_state.get('room_data', {}),
            predicted_state.get('sensor_data', {}), 
            predicted_state.get('devices', []),
            slos
        )
        
        # Calculate composite score
        slo_score = predicted_evaluation.get('overall_compliance', 0.0)
        
        # Factor in agent confidence levels
        agent_confidence = sum(decision.get('confidence', 0.5) for decision in plan.agent_decisions) / len(plan.agent_decisions)
        
        # Factor in action complexity (simpler plans score higher)
        complexity_penalty = min(0.1, len(plan.actions) * 0.02)
        
        # Calculate final score
        composite_score = (slo_score * 0.7 + agent_confidence * 0.3) - complexity_penalty
        
        plan.score = max(0.0, min(1.0, composite_score))
        plan.confidence = agent_confidence
        plan.slo_compliance = predicted_evaluation
        
        return plan.score
    
    def _simulate_plan_impact(self, plan: DecisionPlan, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the expected impact of executing a decision plan"""
        
        # Create a copy of current state
        predicted_state = {
            'room_data': current_state.get('room_data', {}).copy(),
            'sensor_data': current_state.get('sensor_data', {}).copy(),
            'devices': [d.copy() for d in current_state.get('devices', [])]
        }
        
        # Apply each action in the plan
        for action in plan.actions:
            self._apply_action_to_state(action, predicted_state)
        
        # Simulate environmental changes
        self._simulate_environmental_response(predicted_state)
        
        return predicted_state
    
    def _apply_action_to_state(self, action: Dict[str, Any], state: Dict[str, Any]):
        """Apply a single action to the simulated state"""
        
        device_id = action.get('device_id')
        action_type = action.get('action')
        parameters = action.get('parameters', {})
        
        # Find and update the device
        for device in state['devices']:
            if device.get('id') == device_id:
                if action_type == 'turn_on':
                    device['status'] = 'ON'
                elif action_type == 'turn_off':
                    device['status'] = 'OFF'
                elif action_type == 'dim':
                    device['status'] = 'ON'
                    device['brightness'] = parameters.get('brightness', 0.5)
                elif action_type == 'set_temperature':
                    device['target_temperature'] = parameters.get('temperature', 23)
                # Add more action types as needed
                break
    
    def _simulate_environmental_response(self, state: Dict[str, Any]):
        """Simulate how environment responds to device changes"""
        
        sensor_data = state['sensor_data']
        devices = state['devices']
        
        # Simulate temperature changes based on HVAC
        hvac_devices = [d for d in devices if d.get('type') == 'HVAC' and d.get('status') == 'ON']
        if hvac_devices:
            target_temp = sum(d.get('target_temperature', 23) for d in hvac_devices) / len(hvac_devices)
            current_temp = sensor_data.get('temperature', 22)
            # Simple temperature simulation - move 20% towards target
            sensor_data['temperature'] = current_temp + (target_temp - current_temp) * 0.2
        
        # Simulate CO2 changes based on ventilation
        airflow_devices = [d for d in devices if d.get('type') == 'AirFlow' and d.get('status') == 'ON']
        if airflow_devices:
            current_co2 = sensor_data.get('co2', 400)
            # Ventilation reduces CO2
            sensor_data['co2'] = max(350, current_co2 - len(airflow_devices) * 50)
        
        # Simulate humidity changes
        if hvac_devices:
            current_humidity = sensor_data.get('humidity', 50)
            # HVAC tends to dehumidify slightly
            sensor_data['humidity'] = max(30, current_humidity - 2)


class MultiAgentCoordinator:
    """Coordinates decisions from all smart building agents"""
    
    def __init__(self):
        self.agents = {
            'security': SecurityAgent(),
            'comfort': ComfortAgent(), 
            'energy': EnergyAgent(),
            'emergency': EmergencyAgent(),
            'environmental': EnvironmentalAgent(),
            'occupancy': OccupancyAgent()
        }
        self.conflict_resolver = ConflictResolver()
        self.plan_scorer = DecisionPlanScorer()
        self.slo_service = SLOService()
    
    async def coordinate_decisions(self, context: Dict[str, Any], 
                                 slos: List[SLO], 
                                 resolution_strategies: List[str] = None) -> List[DecisionPlan]:
        """
        Coordinate decisions from all agents and generate ranked decision plans
        
        Args:
            context: Current room and sensor state
            slos: Active SLOs to evaluate against
            resolution_strategies: List of conflict resolution strategies to try
            
        Returns:
            List of ranked decision plans
        """
        
        if resolution_strategies is None:
            resolution_strategies = ['priority_weighted', 'safety_first', 'energy_balance']
        
        # Step 1: Get decisions from all agents
        agent_decisions = await self._collect_agent_decisions(context)
        
        # Step 2: Generate decision plans using different resolution strategies
        decision_plans = []
        
        for strategy in resolution_strategies:
            plan_id = f"{strategy}_{datetime.now().strftime('%H%M%S')}"
            
            # Resolve conflicts using this strategy
            resolution_result = self.conflict_resolver.resolve_conflicts(agent_decisions, strategy)
            
            # Create decision plan
            plan = DecisionPlan(
                plan_id=plan_id,
                agent_decisions=agent_decisions,
                slo_compliance={},
                metadata={
                    'resolution_strategy': strategy,
                    'conflicts_resolved': len(resolution_result.get('conflicts', [])),
                    'total_actions': len(resolution_result.get('resolved_actions', []))
                }
            )
            
            plan.actions = resolution_result.get('resolved_actions', [])
            plan.reasoning = f"Plan resolved using {strategy} strategy with {len(plan.actions)} actions"
            
            # Score the plan
            self.plan_scorer.score_decision_plan(plan, context, slos)
            
            decision_plans.append(plan)
        
        # Step 3: Rank plans by score
        decision_plans.sort(key=lambda p: p.score, reverse=True)
        
        # Step 4: Add execution recommendations
        self._add_execution_recommendations(decision_plans, context, slos)
        
        return decision_plans
    
    async def _collect_agent_decisions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect decisions from all agents in parallel"""
        
        decision_tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(agent.make_decision(context))
            decision_tasks.append(task)
        
        # Wait for all agent decisions
        agent_results = await asyncio.gather(*decision_tasks, return_exceptions=True)
        
        # Filter out exceptions and format results
        valid_decisions = []
        for i, result in enumerate(agent_results):
            if isinstance(result, Exception):
                print(f"Error from {list(self.agents.keys())[i]} agent: {result}")
                continue
            
            if isinstance(result, dict):
                valid_decisions.append(result)
        
        return valid_decisions
    
    def _add_execution_recommendations(self, plans: List[DecisionPlan], 
                                     context: Dict[str, Any], slos: List[SLO]):
        """Add execution recommendations to decision plans"""
        
        for i, plan in enumerate(plans):
            # Determine execution mode recommendation
            if plan.score >= 0.9 and plan.confidence >= 0.85:
                plan.metadata['execution_recommendation'] = 'AUTO'
                plan.metadata['recommendation_reason'] = 'High confidence and SLO compliance'
            elif plan.score >= 0.7 and plan.confidence >= 0.7:
                plan.metadata['execution_recommendation'] = 'REVIEW'
                plan.metadata['recommendation_reason'] = 'Good plan, recommended for manual review'
            else:
                plan.metadata['execution_recommendation'] = 'MANUAL'
                plan.metadata['recommendation_reason'] = 'Requires manual evaluation'
            
            # Add ranking info
            plan.metadata['rank'] = i + 1
            plan.metadata['total_plans'] = len(plans)
            
            # Add SLO impact summary
            if plan.slo_compliance:
                violations = plan.slo_compliance.get('violations', [])
                plan.metadata['slo_violations'] = len(violations)
                plan.metadata['critical_violations'] = len([v for v in violations if v.get('severity') == 'critical'])
    
    def get_execution_summary(self, plans: List[DecisionPlan]) -> Dict[str, Any]:
        """Get a summary for decision execution"""
        
        if not plans:
            return {
                'status': 'no_plans',
                'message': 'No decision plans available'
            }
        
        best_plan = plans[0]
        
        return {
            'status': 'plans_available',
            'total_plans': len(plans),
            'best_plan': {
                'plan_id': best_plan.plan_id,
                'score': best_plan.score,
                'confidence': best_plan.confidence,
                'execution_recommendation': best_plan.metadata.get('execution_recommendation'),
                'total_actions': len(best_plan.actions),
                'slo_violations': best_plan.metadata.get('slo_violations', 0)
            },
            'auto_executable': best_plan.metadata.get('execution_recommendation') == 'AUTO',
            'requires_review': any(p.metadata.get('execution_recommendation') == 'REVIEW' for p in plans[:3])
        }
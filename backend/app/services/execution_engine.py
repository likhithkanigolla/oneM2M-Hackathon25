"""
Decision Execution Engine

This module handles the execution of approved decision plans,
device control, and monitoring of execution results.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

from .decision_coordinator import DecisionPlan
from ..models.device import Device


class ExecutionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ActionResult:
    """Represents the result of executing a single device action"""
    
    def __init__(self, action: Dict[str, Any]):
        self.action = action
        self.device_id = action.get('device_id')
        self.action_type = action.get('action')
        self.status = ExecutionStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = None
        self.response_data = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'device_id': self.device_id,
            'action_type': self.action_type,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time_ms': self._get_execution_time_ms(),
            'error_message': self.error_message,
            'response_data': self.response_data,
            'action': self.action
        }
    
    def _get_execution_time_ms(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None


class ExecutionPlan:
    """Represents the execution status of a complete decision plan"""
    
    def __init__(self, decision_plan: DecisionPlan, execution_mode: str = "MANUAL"):
        self.plan_id = decision_plan.plan_id
        self.decision_plan = decision_plan
        self.execution_mode = execution_mode  # AUTO, MANUAL, REVIEW
        self.status = ExecutionStatus.PENDING
        self.action_results: List[ActionResult] = []
        self.start_time = None
        self.end_time = None
        self.executor = None
        self.approval_required = execution_mode != "AUTO"
        self.approved = False
        self.approved_by = None
        self.approval_time = None
        
        # Create action results for each action in the plan
        for action in decision_plan.actions:
            self.action_results.append(ActionResult(action))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_id': self.plan_id,
            'execution_mode': self.execution_mode,
            'status': self.status.value,
            'approval_required': self.approval_required,
            'approved': self.approved,
            'approved_by': self.approved_by,
            'approval_time': self.approval_time.isoformat() if self.approval_time else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_time_ms': self._get_execution_time_ms(),
            'total_actions': len(self.action_results),
            'completed_actions': len([r for r in self.action_results if r.status == ExecutionStatus.COMPLETED]),
            'failed_actions': len([r for r in self.action_results if r.status == ExecutionStatus.FAILED]),
            'action_results': [r.to_dict() for r in self.action_results],
            'plan_score': self.decision_plan.score,
            'plan_confidence': self.decision_plan.confidence
        }
    
    def _get_execution_time_ms(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None
    
    def get_progress_percentage(self) -> float:
        if not self.action_results:
            return 0.0
        completed = len([r for r in self.action_results if r.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]])
        return (completed / len(self.action_results)) * 100


class DeviceController:
    """Handles actual device control operations"""
    
    def __init__(self):
        self.device_timeouts = {
            'HVAC': 10.0,       # HVAC operations can take longer
            'Lighting': 3.0,     # Lighting should be fast
            'AirFlow': 5.0,      # Airflow moderate
            'Security': 5.0,     # Security moderate
            'Emergency': 15.0    # Emergency systems may take longer
        }
    
    async def execute_device_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single device action
        
        This is a simulation - in real implementation, this would
        interface with actual IoT devices via protocols like MQTT, CoAP, etc.
        """
        
        device_id = action.get('device_id')
        action_type = action.get('action')
        parameters = action.get('parameters', {})
        device_type = action.get('device_type', 'Unknown')
        
        # Simulate action execution time
        execution_time = self.device_timeouts.get(device_type, 3.0)
        
        try:
            # Simulate device communication delay
            await asyncio.sleep(min(execution_time, 2.0))  # Cap simulation time
            
            # Simulate different response patterns based on action type
            response_data = await self._simulate_device_response(device_id, action_type, parameters, device_type)
            
            return {
                'success': True,
                'device_id': device_id,
                'action_type': action_type,
                'response_data': response_data,
                'execution_time_ms': execution_time * 1000
            }
            
        except Exception as e:
            return {
                'success': False,
                'device_id': device_id,
                'action_type': action_type,
                'error': str(e),
                'execution_time_ms': execution_time * 1000
            }
    
    async def _simulate_device_response(self, device_id: str, action_type: str, 
                                      parameters: Dict[str, Any], device_type: str) -> Dict[str, Any]:
        """Simulate device response patterns"""
        
        base_response = {
            'device_id': device_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        if action_type == 'turn_on':
            base_response.update({
                'new_status': 'ON',
                'power_consumption': self._simulate_power_usage(device_type, True)
            })
        elif action_type == 'turn_off':
            base_response.update({
                'new_status': 'OFF',
                'power_consumption': 0
            })
        elif action_type == 'dim':
            brightness = parameters.get('brightness', 0.5)
            base_response.update({
                'new_status': 'ON',
                'brightness': brightness,
                'power_consumption': self._simulate_power_usage(device_type, True) * brightness
            })
        elif action_type == 'set_temperature':
            target_temp = parameters.get('temperature', 23)
            base_response.update({
                'target_temperature': target_temp,
                'current_temperature': target_temp - 1.0,  # Simulate lag
                'heating_cooling_active': True
            })
        elif action_type == 'increase_ventilation':
            level = parameters.get('ventilation_level', 'medium')
            base_response.update({
                'ventilation_level': level,
                'fan_speed': self._get_fan_speed_for_level(level),
                'air_flow_rate': self._get_air_flow_for_level(level)
            })
        
        # Add random simulation of occasional failures (5% failure rate)
        import random
        if random.random() < 0.05:
            raise Exception(f"Simulated device communication failure for {device_id}")
        
        return base_response
    
    def _simulate_power_usage(self, device_type: str, is_on: bool) -> float:
        """Simulate power consumption values"""
        if not is_on:
            return 0.0
            
        base_power = {
            'HVAC': 2500.0,      # Watts
            'Lighting': 60.0,     # Watts
            'AirFlow': 150.0,     # Watts
            'Security': 25.0,     # Watts
            'Emergency': 100.0    # Watts
        }
        return base_power.get(device_type, 50.0)
    
    def _get_fan_speed_for_level(self, level: str) -> int:
        """Convert ventilation level to fan speed"""
        level_map = {'low': 1, 'medium': 2, 'high': 3, 'max': 4}
        return level_map.get(level, 2)
    
    def _get_air_flow_for_level(self, level: str) -> float:
        """Convert ventilation level to air flow rate (CFM)"""
        level_map = {'low': 100.0, 'medium': 200.0, 'high': 350.0, 'max': 500.0}
        return level_map.get(level, 200.0)


class DecisionExecutionEngine:
    """Main execution engine for decision plans"""
    
    def __init__(self):
        self.device_controller = DeviceController()
        self.active_executions: Dict[str, ExecutionPlan] = {}
        self.execution_history: List[ExecutionPlan] = []
        self.max_parallel_executions = 5
    
    async def execute_plan(self, decision_plan: DecisionPlan, 
                          execution_mode: str = "MANUAL", 
                          executor: str = None) -> ExecutionPlan:
        """
        Execute a decision plan
        
        Args:
            decision_plan: The plan to execute
            execution_mode: AUTO, MANUAL, or REVIEW
            executor: Username of the person executing (for audit trail)
            
        Returns:
            ExecutionPlan with results
        """
        
        execution_plan = ExecutionPlan(decision_plan, execution_mode)
        execution_plan.executor = executor
        execution_plan.start_time = datetime.now()
        
        # Check if approval is required
        if execution_plan.approval_required and not execution_plan.approved:
            execution_plan.status = ExecutionStatus.PENDING
            self.active_executions[execution_plan.plan_id] = execution_plan
            return execution_plan
        
        # Execute the plan
        await self._execute_plan_actions(execution_plan)
        
        return execution_plan
    
    async def approve_and_execute_plan(self, plan_id: str, approved_by: str) -> Optional[ExecutionPlan]:
        """Approve a pending execution plan and execute it"""
        
        execution_plan = self.active_executions.get(plan_id)
        if not execution_plan:
            return None
        
        execution_plan.approved = True
        execution_plan.approved_by = approved_by
        execution_plan.approval_time = datetime.now()
        
        # Execute the approved plan
        await self._execute_plan_actions(execution_plan)
        
        return execution_plan
    
    async def _execute_plan_actions(self, execution_plan: ExecutionPlan):
        """Execute all actions in a plan"""
        
        execution_plan.status = ExecutionStatus.IN_PROGRESS
        
        try:
            # Execute actions in parallel (with concurrency limit)
            semaphore = asyncio.Semaphore(self.max_parallel_executions)
            
            async def execute_single_action(action_result: ActionResult):
                async with semaphore:
                    await self._execute_single_action(action_result)
            
            # Create tasks for all actions
            tasks = [execute_single_action(action_result) for action_result in execution_plan.action_results]
            
            # Wait for all actions to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Determine overall execution status
            failed_actions = [r for r in execution_plan.action_results if r.status == ExecutionStatus.FAILED]
            
            if not failed_actions:
                execution_plan.status = ExecutionStatus.COMPLETED
            elif len(failed_actions) < len(execution_plan.action_results):
                execution_plan.status = ExecutionStatus.COMPLETED  # Partial success
            else:
                execution_plan.status = ExecutionStatus.FAILED
        
        except Exception as e:
            execution_plan.status = ExecutionStatus.FAILED
            print(f"Execution plan failed: {e}")
        
        finally:
            execution_plan.end_time = datetime.now()
            
            # Move to history
            self.execution_history.append(execution_plan)
            if execution_plan.plan_id in self.active_executions:
                del self.active_executions[execution_plan.plan_id]
    
    async def _execute_single_action(self, action_result: ActionResult):
        """Execute a single device action"""
        
        action_result.status = ExecutionStatus.IN_PROGRESS
        action_result.start_time = datetime.now()
        
        try:
            # Execute the device action
            result = await self.device_controller.execute_device_action(action_result.action)
            
            if result.get('success', False):
                action_result.status = ExecutionStatus.COMPLETED
                action_result.response_data = result.get('response_data')
            else:
                action_result.status = ExecutionStatus.FAILED
                action_result.error_message = result.get('error', 'Unknown error')
        
        except Exception as e:
            action_result.status = ExecutionStatus.FAILED
            action_result.error_message = str(e)
        
        finally:
            action_result.end_time = datetime.now()
    
    def get_execution_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of an execution plan"""
        
        # Check active executions
        if plan_id in self.active_executions:
            return self.active_executions[plan_id].to_dict()
        
        # Check execution history
        for execution in self.execution_history:
            if execution.plan_id == plan_id:
                return execution.to_dict()
        
        return None
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all execution plans pending approval"""
        
        pending = []
        for execution in self.active_executions.values():
            if execution.approval_required and not execution.approved:
                pending.append(execution.to_dict())
        
        return pending
    
    def cancel_execution(self, plan_id: str, cancelled_by: str = None) -> bool:
        """Cancel a pending or in-progress execution"""
        
        if plan_id in self.active_executions:
            execution = self.active_executions[plan_id]
            execution.status = ExecutionStatus.CANCELLED
            execution.end_time = datetime.now()
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[plan_id]
            
            return True
        
        return False
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of all execution activity"""
        
        active_count = len(self.active_executions)
        pending_approval = len([e for e in self.active_executions.values() if e.approval_required and not e.approved])
        
        recent_history = self.execution_history[-10:]  # Last 10 executions
        success_rate = 0.0
        
        if recent_history:
            successful = len([e for e in recent_history if e.status == ExecutionStatus.COMPLETED])
            success_rate = successful / len(recent_history)
        
        return {
            'active_executions': active_count,
            'pending_approval': pending_approval,
            'recent_success_rate': success_rate,
            'total_executions_today': len([e for e in self.execution_history 
                                         if e.start_time and e.start_time.date() == datetime.now().date()]),
            'average_execution_time_ms': self._calculate_average_execution_time()
        }
    
    def _calculate_average_execution_time(self) -> float:
        """Calculate average execution time for completed plans"""
        
        completed_executions = [e for e in self.execution_history 
                              if e.status == ExecutionStatus.COMPLETED and e.start_time and e.end_time]
        
        if not completed_executions:
            return 0.0
        
        total_time = sum((e.end_time - e.start_time).total_seconds() * 1000 for e in completed_executions)
        return total_time / len(completed_executions)
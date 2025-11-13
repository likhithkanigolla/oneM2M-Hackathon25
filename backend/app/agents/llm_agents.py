"""
Specialized LLM Agents for Smart Room Decision Making

This module contains implementations of different LLM agents,
each designed for specific aspects of smart room management.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
from .agent_config import AgentType, AgentRegistry
from .gemini_client import get_gemini_client, is_gemini_available

class SecurityAgent(BaseAgent):
    """Agent focused on security and surveillance requirements"""
    
    def __init__(self, agent_id: str = "security_agent"):
        super().__init__(agent_id)
        self.config = AgentRegistry.get_agent_config(AgentType.SECURITY)
        self.agent_type = AgentType.SECURITY
        self.gemini_client = get_gemini_client()
    
    async def make_decision(self, context: dict) -> dict:
        """
        Make security-focused decisions using Google Gemini LLM
        """
        # Use LLM if available, otherwise fallback to rule-based logic
        if self.gemini_client and is_gemini_available():
            return await self._make_llm_decision(context)
        else:
            return await self._make_fallback_decision(context)
    
    async def _make_llm_decision(self, context: dict) -> dict:
        """Generate decision using Gemini LLM"""
        try:
            # Load security agent prompt
            prompt = self._load_agent_prompt()
            
            # Generate decision using Gemini
            llm_response = await self.gemini_client.generate_decision(prompt, context)
            
            # Format response for decision engine
            decision = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "priority": self.config.priority_weight,
                "timestamp": datetime.now().isoformat(),
                "decisions": llm_response.get("decisions", []),
                "reasoning": llm_response.get("reasoning", "Security agent decision"),
                "scores": llm_response.get("scores", {"comfort": 0.2, "energy": 0.1, "reliability": 0.9, "security": 1.0}),
                "confidence": llm_response.get("confidence", 0.8)
            }
            
            return decision
            
        except Exception as e:
            print(f"Error in SecurityAgent LLM decision: {e}")
            return await self._make_fallback_decision(context)
    
    def _load_agent_prompt(self) -> str:
        """Load agent-specific prompt template"""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "security_agent_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default prompt if file not found"""
        return """
You are a Security Agent responsible for building security and surveillance.

MISSION: Ensure optimal security conditions while balancing other building needs.

KEY RESPONSIBILITIES:
- Maintain adequate lighting for surveillance
- Monitor and respond to security device status
- Ensure emergency access and safety compliance
- Balance security needs with energy efficiency

DECISION PRINCIPLES:
1. Security requirements always take precedence in emergencies
2. Maintain minimum lighting levels for surveillance
3. Respond to security device malfunctions immediately
4. Consider occupancy patterns for security optimization

Analyze the current context and provide specific device actions to maintain security standards.
"""
    
    async def _make_fallback_decision(self, context: dict) -> dict:
        """Fallback rule-based decision when LLM unavailable"""
        room_data = context.get('room_data', {})
        devices = context.get('devices', [])
        slos = context.get('slos', [])
        sensor_data = context.get('sensor_data', {})
        
        # Security-specific logic
        lighting_devices = [d for d in devices if d.get('type') == 'Lighting']
        security_devices = [d for d in devices if d.get('type') == 'Security']
        
        decisions = []
        reasoning_parts = []
        
        # Check if security SLO requires at least one light on
        security_slos = [slo for slo in slos if 'security' in slo.get('name', '').lower()]
        
        if security_slos and lighting_devices:
            # Ensure at least one light is on for surveillance
            lights_on = [d for d in lighting_devices if d.get('status') == 'ON']
            if not lights_on and lighting_devices:
                decisions.append({
                    "device_id": lighting_devices[0].get('id'),
                    "action": "turn_on",
                    "parameters": {"brightness": 0.3},
                    "priority": 0.9
                })
                reasoning_parts.append("Activating minimum lighting for security surveillance")
        
        # Check security device status
        for device in security_devices:
            if device.get('status') == 'OFF':
                decisions.append({
                    "device_id": device.get('id'),
                    "action": "turn_on",
                    "parameters": {},
                    "priority": 0.8
                })
                reasoning_parts.append(f"Activating {device.get('name')} for security coverage")
        
        decision = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "priority": self.config.priority_weight,
            "timestamp": datetime.now().isoformat(),
            "decisions": decisions,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Security conditions maintained",
            "scores": {"comfort": 0.2, "energy": 0.1, "reliability": 0.9, "security": 1.0},
            "confidence": 0.7
        }
        
        return decision



class EmergencyAgent(BaseAgent):
    """Agent focused on emergency response and safety"""
    
    def __init__(self, agent_id: str = "emergency_agent"):
        super().__init__(agent_id)
        self.config = AgentRegistry.get_agent_config(AgentType.EMERGENCY_RESPONSE)
        self.agent_type = AgentType.EMERGENCY_RESPONSE
        self.gemini_client = get_gemini_client()
    
    async def make_decision(self, context: dict) -> dict:
        """Make emergency-focused decisions using Google Gemini LLM"""
        if self.gemini_client and is_gemini_available():
            return await self._make_llm_decision(context)
        else:
            return await self._make_fallback_decision(context)
    
    async def _make_llm_decision(self, context: dict) -> dict:
        """Generate decision using Gemini LLM"""
        try:
            prompt = self._load_agent_prompt()
            llm_response = await self.gemini_client.generate_decision(prompt, context)
            
            decision = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "priority": self.config.priority_weight,
                "timestamp": datetime.now().isoformat(),
                "decisions": llm_response.get("decisions", []),
                "reasoning": llm_response.get("reasoning", "Emergency agent decision"),
                "scores": llm_response.get("scores", {"comfort": 0.3, "energy": 0.2, "reliability": 1.0, "security": 0.9}),
                "confidence": llm_response.get("confidence", 0.8),
                "emergency_level": llm_response.get("emergency_level", 0)
            }
            
            return decision
            
        except Exception as e:
            print(f"Error in EmergencyAgent LLM decision: {e}")
            return await self._make_fallback_decision(context)
    
    def _load_agent_prompt(self) -> str:
        """Load agent-specific prompt template"""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "emergency_agent_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default emergency agent prompt"""
        return """
You are an Emergency Agent responsible for safety and crisis response in smart buildings.

MISSION: Ensure immediate safety response and maintain critical building systems during emergencies.

KEY RESPONSIBILITIES:
- Monitor for emergency conditions (fire, gas leaks, security breaches)
- Ensure emergency lighting and exits are accessible
- Coordinate with safety systems and protocols
- Override other agents during critical situations

DECISION PRINCIPLES:
1. Safety always takes absolute priority
2. Immediate response to emergency conditions
3. Maintain emergency lighting and communications
4. Override all other agent decisions in crisis

Analyze the current context and provide specific device actions for emergency response.
"""
    
    async def _make_fallback_decision(self, context: dict) -> dict:
        """Fallback rule-based decision"""
        sensor_data = context.get('sensor_data', {})
        devices = context.get('devices', [])
        
        decisions = []
        reasoning_parts = []
        emergency_level = 0
        
        # Check for emergency conditions
        co2_level = sensor_data.get('co2', 0)
        temperature = sensor_data.get('temperature', 22)
        
        if co2_level > 1000:  # High CO2 - potential emergency
            emergency_level = 3
            hvac_devices = [d for d in devices if d.get('type') == 'HVAC']
            for hvac in hvac_devices:
                decisions.append({
                    "device_id": hvac.get('id'),
                    "action": "emergency_ventilation",
                    "parameters": {"mode": "max_ventilation"},
                    "priority": 1.0
                })
            reasoning_parts.append("Emergency ventilation activated - high CO2 levels detected")
        
        if temperature > 35:  # Extreme temperature
            emergency_level = max(emergency_level, 4)
            reasoning_parts.append("Extreme temperature detected - emergency cooling required")
        
        decision = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "priority": self.config.priority_weight,
            "timestamp": datetime.now().isoformat(),
            "decisions": decisions,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No emergency conditions detected",
            "scores": {"comfort": 0.3, "energy": 0.2, "reliability": 1.0, "security": 0.9},
            "confidence": 0.9,
            "emergency_level": emergency_level
        }
        
        return decision


class EnvironmentalAgent(BaseAgent):
    """Agent focused on environmental conditions and air quality"""
    
    def __init__(self, agent_id: str = "environmental_agent"):
        super().__init__(agent_id)
        self.config = AgentRegistry.get_agent_config(AgentType.ENVIRONMENTAL)
        self.agent_type = AgentType.ENVIRONMENTAL
        self.gemini_client = get_gemini_client()
    
    async def make_decision(self, context: dict) -> dict:
        """Make environmental-focused decisions using Google Gemini LLM"""
        if self.gemini_client and is_gemini_available():
            return await self._make_llm_decision(context)
        else:
            return await self._make_fallback_decision(context)
    
    async def _make_llm_decision(self, context: dict) -> dict:
        """Generate decision using Gemini LLM"""
        try:
            prompt = self._load_agent_prompt()
            llm_response = await self.gemini_client.generate_decision(prompt, context)
            
            decision = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "priority": self.config.priority_weight,
                "timestamp": datetime.now().isoformat(),
                "decisions": llm_response.get("decisions", []),
                "reasoning": llm_response.get("reasoning", "Environmental agent decision"),
                "scores": llm_response.get("scores", {"comfort": 0.8, "energy": 0.5, "reliability": 0.7, "security": 0.3}),
                "confidence": llm_response.get("confidence", 0.8)
            }
            
            return decision
            
        except Exception as e:
            print(f"Error in EnvironmentalAgent LLM decision: {e}")
            return await self._make_fallback_decision(context)
    
    def _load_agent_prompt(self) -> str:
        """Load agent-specific prompt template"""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "environmental_agent_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default environmental agent prompt"""
        return """
You are an Environmental Agent responsible for air quality and environmental health.

MISSION: Maintain optimal indoor environmental conditions for health and productivity.

KEY RESPONSIBILITIES:
- Monitor and control air quality parameters
- Manage humidity and ventilation systems
- Respond to environmental hazards
- Optimize indoor environmental health

DECISION PRINCIPLES:
1. Maintain healthy air quality levels
2. Control humidity within optimal ranges
3. Ensure adequate ventilation for occupants
4. Balance environmental quality with energy efficiency

Analyze the current context and provide specific device actions for environmental optimization.
"""
    
    async def _make_fallback_decision(self, context: dict) -> dict:
        """Fallback rule-based decision"""
        sensor_data = context.get('sensor_data', {})
        devices = context.get('devices', [])
        
        decisions = []
        reasoning_parts = []
        
        humidity = sensor_data.get('humidity', 50)
        co2_level = sensor_data.get('co2', 400)
        
        hvac_devices = [d for d in devices if d.get('type') == 'HVAC']
        
        # Humidity control
        if humidity > 70:
            for hvac in hvac_devices:
                decisions.append({
                    "device_id": hvac.get('id'),
                    "action": "dehumidify",
                    "parameters": {"target_humidity": 60},
                    "priority": 0.6
                })
            reasoning_parts.append("High humidity detected - activating dehumidification")
        elif humidity < 30:
            for hvac in hvac_devices:
                decisions.append({
                    "device_id": hvac.get('id'),
                    "action": "humidify",
                    "parameters": {"target_humidity": 45},
                    "priority": 0.6
                })
            reasoning_parts.append("Low humidity detected - activating humidification")
        
        # CO2 control
        if co2_level > 800:
            for hvac in hvac_devices:
                decisions.append({
                    "device_id": hvac.get('id'),
                    "action": "increase_ventilation",
                    "parameters": {"ventilation_level": "high"},
                    "priority": 0.7
                })
            reasoning_parts.append("Elevated CO2 levels - increasing ventilation")
        
        decision = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "priority": self.config.priority_weight,
            "timestamp": datetime.now().isoformat(),
            "decisions": decisions,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Environmental conditions optimal",
            "scores": {"comfort": 0.8, "energy": 0.5, "reliability": 0.7, "security": 0.3},
            "confidence": 0.7
        }
        
        return decision


class OccupancyAgent(BaseAgent):
    """Agent focused on occupancy patterns and space utilization"""
    
    def __init__(self, agent_id: str = "occupancy_agent"):
        super().__init__(agent_id)
        self.config = AgentRegistry.get_agent_config(AgentType.OCCUPANCY)
        self.agent_type = AgentType.OCCUPANCY
        self.gemini_client = get_gemini_client()
    
    async def make_decision(self, context: dict) -> dict:
        """Make occupancy-focused decisions using Google Gemini LLM"""
        if self.gemini_client and is_gemini_available():
            return await self._make_llm_decision(context)
        else:
            return await self._make_fallback_decision(context)
    
    async def _make_llm_decision(self, context: dict) -> dict:
        """Generate decision using Gemini LLM"""
        try:
            prompt = self._load_agent_prompt()
            llm_response = await self.gemini_client.generate_decision(prompt, context)
            
            decision = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "priority": self.config.priority_weight,
                "timestamp": datetime.now().isoformat(),
                "decisions": llm_response.get("decisions", []),
                "reasoning": llm_response.get("reasoning", "Occupancy agent decision"),
                "scores": llm_response.get("scores", {"comfort": 0.7, "energy": 0.8, "reliability": 0.6, "security": 0.5}),
                "confidence": llm_response.get("confidence", 0.8)
            }
            
            return decision
            
        except Exception as e:
            print(f"Error in OccupancyAgent LLM decision: {e}")
            return await self._make_fallback_decision(context)
    
    def _load_agent_prompt(self) -> str:
        """Load agent-specific prompt template"""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "occupancy_agent_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default occupancy agent prompt"""
        return """
You are an Occupancy Agent responsible for space utilization and occupancy-based optimization.

MISSION: Optimize building systems based on occupancy patterns and space utilization.

KEY RESPONSIBILITIES:
- Adjust systems based on current occupancy levels
- Predict and prepare for occupancy changes
- Optimize resource allocation per space usage
- Balance individual and collective needs

DECISION PRINCIPLES:
1. Scale systems based on actual occupancy
2. Anticipate occupancy pattern changes
3. Optimize for both occupied and vacant periods
4. Balance individual comfort with group efficiency

Analyze the current context and provide specific device actions based on occupancy optimization.
"""
    
    async def _make_fallback_decision(self, context: dict) -> dict:
        """Fallback rule-based decision"""
        sensor_data = context.get('sensor_data', {})
        devices = context.get('devices', [])
        occupancy = sensor_data.get('occupancy', 0)

        # Device groups
        lighting_devices = [d for d in devices if d.get('type') == 'Lighting']
        hvac_devices = [d for d in devices if d.get('type') == 'HVAC']
        security_devices = [d for d in devices if d.get('type') == 'Security']

        # Build base decision structure
        decision = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "priority": self.config.priority_weight,
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "reasoning": "",
            "scores": {"comfort": 0.7, "energy": 0.8, "reliability": 0.6, "security": 0.5},
            "confidence": 0.7
        }

        reasoning_parts = []

        if occupancy == 0:
            # Reduce systems for unoccupied space
            for light in lighting_devices:
                if light.get('status') == 'ON':
                    decision["decisions"].append({
                        "device_id": light.get('id'),
                        "action": "dim",
                        "parameters": {"brightness": 0.1},
                        "priority": 0.6
                    })
            reasoning_parts.append("Dimming lights for unoccupied space")

        elif occupancy > 5:  # High occupancy
            # Increase ventilation and lighting
            for hvac in hvac_devices:
                decision["decisions"].append({
                    "device_id": hvac.get('id'),
                    "action": "increase_ventilation",
                    "parameters": {"ventilation_level": "high"},
                    "priority": 0.7
                })
            reasoning_parts.append("Increasing ventilation for high occupancy")

        # Security decision logic: ensure at least one light on for surveillance
        lights_on = sum(1 for light in lighting_devices if light.get('status') == 'ON')
        if lights_on == 0 and lighting_devices:
            # Turn on one light for minimal surveillance
            light = lighting_devices[0]
            decision["decisions"].append({
                "device_id": light.get('id'),
                "action": "turn_on",
                "parameters": {},
                "priority": 0.9,
                "reason": "Security requirement: At least one light must be on for surveillance"
            })
            reasoning_parts.append("Activated minimum lighting for security compliance")
        else:
            reasoning_parts.append(f"Security OK: {lights_on} lights currently on for surveillance.")

        # Ensure security devices are operational
        for sec_device in security_devices:
            if sec_device.get('status') != 'ON':
                decision["decisions"].append({
                    "device_id": sec_device.get('id'),
                    "action": "turn_on",
                    "parameters": {},
                    "priority": 0.8,
                    "reason": "Security device must remain operational"
                })

        decision["reasoning"] = "; ".join(reasoning_parts) if reasoning_parts else "Occupancy-based optimization complete"
        return decision

class ComfortAgent(BaseAgent):
    """Agent focused on occupant comfort optimization"""
    
    def __init__(self, agent_id: str = "comfort_agent"):
        super().__init__(agent_id)
        self.config = AgentRegistry.get_agent_config(AgentType.COMFORT)
        self.agent_type = AgentType.COMFORT
        self.gemini_client = get_gemini_client()
    
    async def make_decision(self, context: dict) -> dict:
        """Make comfort-focused decisions using Google Gemini LLM"""
        if self.gemini_client and is_gemini_available():
            return await self._make_llm_decision(context)
        else:
            return await self._make_fallback_decision(context)
    
    async def _make_llm_decision(self, context: dict) -> dict:
        """Generate decision using Gemini LLM"""
        try:
            prompt = self._load_agent_prompt()
            llm_response = await self.gemini_client.generate_decision(prompt, context)
            
            decision = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "priority": self.config.priority_weight,
                "timestamp": datetime.now().isoformat(),
                "decisions": llm_response.get("decisions", []),
                "reasoning": llm_response.get("reasoning", "Comfort agent decision"),
                "scores": llm_response.get("scores", {"comfort": 1.0, "energy": 0.3, "reliability": 0.7, "security": 0.2}),
                "confidence": llm_response.get("confidence", 0.8)
            }
            
            return decision
            
        except Exception as e:
            print(f"Error in ComfortAgent LLM decision: {e}")
            return await self._make_fallback_decision(context)
    
    def _load_agent_prompt(self) -> str:
        """Load agent-specific prompt template"""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "comfort_agent_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default comfort agent prompt"""
        return """
You are a Comfort Agent responsible for occupant comfort and well-being.

MISSION: Maintain optimal comfort conditions while balancing energy efficiency and other building needs.

KEY RESPONSIBILITIES:
- Manage temperature control systems for optimal comfort
- Ensure proper lighting for activities and wellbeing
- Maintain air quality and circulation
- Respond to occupancy patterns and preferences

DECISION PRINCIPLES:
1. Prioritize occupant comfort within reasonable energy bounds
2. Adjust systems based on occupancy levels and activities
3. Maintain temperature within comfort ranges (22-24°C)
4. Ensure adequate air circulation for occupied spaces

Analyze the current context and provide specific device actions to optimize comfort.
"""
    
    async def _make_fallback_decision(self, context: dict) -> dict:
        """Fallback rule-based decision when LLM unavailable"""
        room_data = context.get('room_data', {})
        devices = context.get('devices', [])
        slos = context.get('slos', [])
        sensor_data = context.get('sensor_data', {})
        
        hvac_devices = [d for d in devices if d.get('type') == 'HVAC']
        lighting_devices = [d for d in devices if d.get('type') == 'Lighting']
        airflow_devices = [d for d in devices if d.get('type') == 'AirFlow']
        
        decision = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "priority": self.config.priority_weight,
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "reasoning": "",
            "scores": {"comfort": 1.0, "energy": 0.4, "reliability": 0.7, "security": 0.3}
        }
        
        # Temperature management
        current_temp = sensor_data.get('temperature', 22)
        target_temp = 23  # Default comfort temperature
        temp_tolerance = 1.0
        
        # Check for meeting SLOs that might specify temperature requirements
        meeting_slos = [slo for slo in slos if 'meeting' in slo.get('name', '').lower() or 'conference' in slo.get('name', '').lower()]
        if meeting_slos:
            target_temp = 22  # Slightly cooler for meetings
        
        if abs(current_temp - target_temp) > temp_tolerance:
            for hvac in hvac_devices:
                if current_temp < target_temp - temp_tolerance:
                    decision["decisions"].append({
                        "device_id": hvac.get('id'),
                        "action": "turn_on",
                        "reason": f"Temperature {current_temp}°C below comfort range. Heating required."
                    })
                elif current_temp > target_temp + temp_tolerance:
                    decision["decisions"].append({
                        "device_id": hvac.get('id'), 
                        "action": "turn_on",
                        "reason": f"Temperature {current_temp}°C above comfort range. Cooling required."
                    })
        
        # Air circulation for occupied rooms
        occupancy = sensor_data.get('occupancy', 0)
        if occupancy > 0:
            for airflow in airflow_devices:
                if airflow.get('status') != 'ON':
                    decision["decisions"].append({
                        "device_id": airflow.get('id'),
                        "action": "turn_on",
                        "reason": "Air circulation required for occupied room"
                    })
        
        decision["reasoning"] = f"Comfort optimization: Target temp {target_temp}°C, Current {current_temp}°C, Occupancy {occupancy}"
        return decision

class EnergyAgent(BaseAgent):
    """Agent focused on energy efficiency and conservation"""
    
    def __init__(self, agent_id: str = "energy_agent"):
        super().__init__(agent_id)
        self.config = AgentRegistry.get_agent_config(AgentType.ENERGY_EFFICIENCY)
        self.agent_type = AgentType.ENERGY_EFFICIENCY
        self.gemini_client = get_gemini_client()
        
    async def make_decision(self, context: dict) -> dict:
        """Make energy-focused decisions using Google Gemini LLM"""
        if self.gemini_client and is_gemini_available():
            return await self._make_llm_decision(context)
        else:
            return await self._make_fallback_decision(context)
    
    async def _make_llm_decision(self, context: dict) -> dict:
        """Generate decision using Gemini LLM"""
        try:
            prompt = self._load_agent_prompt()
            llm_response = await self.gemini_client.generate_decision(prompt, context)
            
            decision = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "priority": self.config.priority_weight,
                "timestamp": datetime.now().isoformat(),
                "decisions": llm_response.get("decisions", []),
                "reasoning": llm_response.get("reasoning", "Energy agent decision"),
                "scores": llm_response.get("scores", {"comfort": 0.3, "energy": 1.0, "reliability": 0.6, "security": 0.4}),
                "confidence": llm_response.get("confidence", 0.8)
            }
            
            return decision
            
        except Exception as e:
            print(f"Error in EnergyAgent LLM decision: {e}")
            return await self._make_fallback_decision(context)
    
    def _load_agent_prompt(self) -> str:
        """Load agent-specific prompt template"""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "energy_agent_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Default energy agent prompt"""
        return """
You are an Energy Agent responsible for optimizing energy consumption and efficiency.

MISSION: Minimize energy usage while maintaining essential building operations and occupant comfort.

KEY RESPONSIBILITIES:
- Optimize power consumption across all building systems
- Implement energy-saving strategies during off-peak hours
- Coordinate with other agents to balance energy vs comfort/security
- Monitor and reduce wasteful energy usage

DECISION PRINCIPLES:
1. Minimize energy consumption without compromising critical operations
2. Turn off non-essential systems in unoccupied areas
3. Optimize HVAC and lighting based on occupancy patterns
4. Consider time-of-use rates and peak demand periods

Analyze the current context and provide specific device actions to optimize energy usage.
"""
    
    async def _make_fallback_decision(self, context: dict) -> dict:
        """Fallback rule-based decision when LLM unavailable"""
        devices = context.get('devices', [])
        sensor_data = context.get('sensor_data', {})
        
        decision = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "priority": self.config.priority_weight,
            "timestamp": datetime.now().isoformat(),
            "decisions": [],
            "reasoning": "",
            "scores": {"comfort": 0.3, "energy": 1.0, "reliability": 0.6, "security": 0.4}
        }
        
        occupancy = sensor_data.get('occupancy', 0)
        current_hour = datetime.now().hour
        
        # Energy saving for unoccupied rooms
        if occupancy == 0:
            # Turn off non-essential devices
            for device in devices:
                if device.get('status') == 'ON' and device.get('type') in ['Lighting', 'AirFlow']:
                    # Don't turn off if security requires it
                    if device.get('type') == 'Lighting':
                        # Keep one light on for security
                        lights_on = [d for d in devices if d.get('type') == 'Lighting' and d.get('status') == 'ON']
                        if len(lights_on) > 1:
                            decision["decisions"].append({
                                "device_id": device.get('id'),
                                "action": "turn_off",
                                "reason": "Energy saving: Room unoccupied, excess lighting not needed"
                            })
                    else:
                        decision["decisions"].append({
                            "device_id": device.get('id'),
                            "action": "turn_off", 
                            "reason": "Energy saving: Room unoccupied"
                        })
        
        # Off-peak hour optimizations
        if current_hour >= 22 or current_hour <= 6:  # Night hours
            for device in devices:
                if device.get('type') == 'HVAC' and device.get('status') == 'ON' and occupancy == 0:
                    decision["decisions"].append({
                        "device_id": device.get('id'),
                        "action": "turn_off",
                        "reason": "Night-time energy saving: HVAC not needed for unoccupied room"
                    })
        
        total_devices_on = sum(1 for d in devices if d.get('status') == 'ON')
        decision["reasoning"] = f"Energy optimization: {total_devices_on} devices active, Occupancy: {occupancy}, Hour: {current_hour}"
        
        return decision
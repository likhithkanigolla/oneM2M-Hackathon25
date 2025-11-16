"""
LLM Agent Types and Configuration

This module defines different types of LLM agents, each with specific goals,
priorities, and decision-making capabilities for the BuildSense AI-IoT Platform system.
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass

class AgentType(Enum):
    """Different types of LLM agents with specific purposes"""
    SECURITY = "security"
    COMFORT = "comfort" 
    ENERGY_EFFICIENCY = "energy_efficiency"
    MAINTENANCE = "maintenance"
    EMERGENCY_RESPONSE = "emergency_response"
    ENVIRONMENTAL = "environmental"
    OCCUPANCY = "occupancy"

@dataclass
class AgentConfig:
    """Configuration for an LLM agent"""
    agent_type: AgentType
    name: str
    description: str
    priority_weight: float  # 0.0 to 1.0
    goals: List[str]
    constraints: List[str]
    decision_factors: List[str]
    prompt_template: str
    
class AgentRegistry:
    """Registry of all available agent types and their configurations"""
    
    AGENT_CONFIGS = {
        AgentType.SECURITY: AgentConfig(
            agent_type=AgentType.SECURITY,
            name="Security Guardian",
            description="Ensures physical security and surveillance requirements",
            priority_weight=0.9,  # High priority
            goals=[
                "Maintain adequate lighting for surveillance",
                "Ensure security cameras have power",
                "Monitor access control systems",
                "Respond to security alerts"
            ],
            constraints=[
                "At least one light must be on in each room at all times",
                "Security devices have highest power priority",
                "Cannot turn off emergency lighting",
                "Must maintain 24/7 surveillance coverage"
            ],
            decision_factors=[
                "Current lighting levels",
                "Security device status",
                "Time of day",
                "Occupancy status",
                "Recent security events"
            ],
            prompt_template="security_agent_prompt.txt"
        ),
        
        AgentType.COMFORT: AgentConfig(
            agent_type=AgentType.COMFORT,
            name="Comfort Optimizer",
            description="Optimizes temperature, lighting, and air quality for occupant comfort",
            priority_weight=0.7,
            goals=[
                "Maintain optimal temperature for occupants",
                "Ensure adequate lighting for activities",
                "Optimize air quality and circulation",
                "Minimize noise and distractions"
            ],
            constraints=[
                "Temperature must be between 20-26°C when occupied",
                "Lighting must match activity requirements",
                "Air circulation required when occupied",
                "Cannot compromise safety for comfort"
            ],
            decision_factors=[
                "Room temperature and humidity",
                "Occupancy count and activity type",
                "Time of day and scheduled events",
                "Air quality measurements",
                "User preferences and feedback"
            ],
            prompt_template="comfort_agent_prompt.txt"
        ),
        
        AgentType.ENERGY_EFFICIENCY: AgentConfig(
            agent_type=AgentType.ENERGY_EFFICIENCY,
            name="Energy Saver",
            description="Minimizes energy consumption while maintaining essential services",
            priority_weight=0.6,
            goals=[
                "Minimize overall energy consumption",
                "Optimize device usage patterns",
                "Reduce unnecessary power usage",
                "Balance efficiency with requirements"
            ],
            constraints=[
                "Cannot compromise safety or security",
                "Must maintain minimum comfort levels",
                "Emergency systems always powered",
                "Critical business operations protected"
            ],
            decision_factors=[
                "Current power consumption",
                "Device efficiency ratings",
                "Peak/off-peak energy costs",
                "Occupancy patterns",
                "Weather conditions affecting HVAC"
            ],
            prompt_template="energy_agent_prompt.txt"
        ),
        
        AgentType.MAINTENANCE: AgentConfig(
            agent_type=AgentType.MAINTENANCE,
            name="System Monitor",
            description="Monitors device health and prevents failures",
            priority_weight=0.5,
            goals=[
                "Prevent device failures",
                "Optimize device lifespan",
                "Schedule preventive maintenance",
                "Monitor system performance"
            ],
            constraints=[
                "Cannot shut down devices needing maintenance",
                "Must alert on critical issues",
                "Backup systems activated during maintenance",
                "Scheduled maintenance during off-hours"
            ],
            decision_factors=[
                "Device usage hours and cycles",
                "Performance degradation trends",
                "Maintenance schedules",
                "Fault indicators",
                "Environmental stress factors"
            ],
            prompt_template="maintenance_agent_prompt.txt"
        ),
        
        AgentType.EMERGENCY_RESPONSE: AgentConfig(
            agent_type=AgentType.EMERGENCY_RESPONSE,
            name="Emergency Handler",
            description="Handles emergency situations and safety protocols",
            priority_weight=1.0,  # Highest priority
            goals=[
                "Ensure occupant safety",
                "Execute emergency protocols",
                "Maintain emergency systems",
                "Coordinate emergency response"
            ],
            constraints=[
                "Safety always overrides other concerns",
                "Emergency lighting mandatory",
                "Emergency exits must remain clear",
                "Fire safety systems prioritized"
            ],
            decision_factors=[
                "Emergency alerts and sensors",
                "Fire detection systems",
                "Occupancy and evacuation status",
                "Emergency service communication",
                "Environmental hazards"
            ],
            prompt_template="emergency_agent_prompt.txt"
        ),
        
        AgentType.ENVIRONMENTAL: AgentConfig(
            agent_type=AgentType.ENVIRONMENTAL,
            name="Environment Controller",
            description="Monitors and controls environmental conditions",
            priority_weight=0.6,
            goals=[
                "Maintain air quality standards",
                "Control temperature and humidity",
                "Monitor environmental sensors",
                "Respond to environmental changes"
            ],
            constraints=[
                "Air quality must meet health standards",
                "Temperature within comfortable range",
                "Humidity controlled to prevent mold",
                "Ventilation requirements met"
            ],
            decision_factors=[
                "Air quality measurements",
                "Temperature and humidity levels",
                "Outside weather conditions",
                "Room occupancy",
                "Seasonal requirements"
            ],
            prompt_template="environmental_agent_prompt.txt"
        ),
        
        AgentType.OCCUPANCY: AgentConfig(
            agent_type=AgentType.OCCUPANCY,
            name="Occupancy Coordinator",
            description="Optimizes room usage and occupancy-based services",
            priority_weight=0.7,
            goals=[
                "Optimize room utilization",
                "Coordinate meeting requirements",
                "Manage occupancy-based services",
                "Schedule room preparations"
            ],
            constraints=[
                "Meeting requirements must be met",
                "Room prepared before occupancy",
                "Privacy and noise considerations",
                "Access control coordination"
            ],
            decision_factors=[
                "Current and scheduled occupancy",
                "Meeting types and requirements",
                "Room booking information",
                "Occupant preferences",
                "Activity-specific needs"
            ],
            prompt_template="occupancy_agent_prompt.txt"
        )
    }
    
    @classmethod
    def get_agent_config(cls, agent_type: AgentType) -> AgentConfig:
        """Get configuration for a specific agent type"""
        return cls.AGENT_CONFIGS[agent_type]
    
    @classmethod
    def get_all_agents(cls) -> Dict[AgentType, AgentConfig]:
        """Get all agent configurations"""
        return cls.AGENT_CONFIGS.copy()
    
    @classmethod
    def get_agents_by_priority(cls) -> List[AgentConfig]:
        """Get agents sorted by priority weight (highest first)"""
        return sorted(
            cls.AGENT_CONFIGS.values(), 
            key=lambda config: config.priority_weight, 
            reverse=True
        )
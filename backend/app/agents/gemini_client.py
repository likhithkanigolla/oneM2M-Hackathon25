"""
Google Gemini API integration for LLM agents

This module provides integration with Google's Gemini API for 
intelligent decision making in smart building management.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime

class GeminiLLMClient:
    """
    Google Gemini API client for LLM agent decision making
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Use Gemini Pro model for decision making
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_decision(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LLM decision using Google Gemini
        
        Args:
            prompt: Formatted prompt for the agent
            context: Decision context data
            
        Returns:
            Parsed decision response
        """
        try:
            # Create the full prompt with context
            full_prompt = self._build_full_prompt(prompt, context)
            
            # Generate response using Gemini
            response = await self._make_api_call(full_prompt)
            
            # Parse and validate response
            decision = self._parse_response(response)
            
            return decision
            
        except Exception as e:
            print(f"Error in Gemini API call: {e}")
            return self._fallback_decision(context)
    
    def _build_full_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Build complete prompt with context data"""
        
        # Format context for the prompt
        context_str = self._format_context(context)
        
        full_prompt = f"""
{prompt}

CURRENT CONTEXT:
{context_str}

IMPORTANT: Respond ONLY with valid JSON in the following format:
{{
    "decisions": [
        {{
            "device_id": "device_identifier",
            "action": "specific_action",
            "parameters": {{"param1": "value1"}},
            "priority": 0.8
        }}
    ],
    "reasoning": "Clear explanation of decision logic and SLO considerations",
    "confidence": 0.85,
    "scores": {{
        "comfort": 0.8,
        "energy": 0.7,
        "reliability": 0.9,
        "security": 0.8
    }},
    "emergency_level": 0
}}

Do not include any text before or after the JSON response.
"""
        
        return full_prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data for prompt inclusion"""
        
        formatted_sections = []
        
        # Room information
        if 'room_data' in context:
            room = context['room_data']
            formatted_sections.append(f"Room: {room.get('name', 'Unknown')} (ID: {room.get('id', 'N/A')})")
        
        # Device status
        if 'devices' in context:
            devices = context['devices']
            device_info = []
            for device in devices:
                status = device.get('status', 'unknown')
                device_info.append(f"- {device.get('name', 'Unknown')} ({device.get('type', 'Unknown')}): {status}")
            if device_info:
                formatted_sections.append("Devices:\n" + "\n".join(device_info))
        
        # SLO requirements
        if 'slos' in context:
            slos = context['slos']
            slo_info = []
            for slo in slos:
                slo_info.append(f"- {slo.get('name', 'Unknown')}: Target {slo.get('target_value', 'N/A')} {slo.get('unit', '')}")
            if slo_info:
                formatted_sections.append("Active SLOs:\n" + "\n".join(slo_info))
        
        # Sensor data
        if 'sensor_data' in context:
            sensor = context['sensor_data']
            sensor_info = []
            if 'temperature' in sensor:
                sensor_info.append(f"Temperature: {sensor['temperature']}°C")
            if 'humidity' in sensor:
                sensor_info.append(f"Humidity: {sensor['humidity']}%")
            if 'occupancy' in sensor:
                sensor_info.append(f"Occupancy: {sensor['occupancy']} people")
            if 'light_level' in sensor:
                sensor_info.append(f"Light Level: {sensor['light_level']} lux")
            if sensor_info:
                formatted_sections.append("Sensors: " + ", ".join(sensor_info))
        
        # Scenarios
        if 'scenarios' in context:
            scenarios = context['scenarios']
            if scenarios:
                scenario_names = [s.get('name', 'Unknown') for s in scenarios]
                formatted_sections.append("Active Scenarios: " + ", ".join(scenario_names))
        
        return "\n\n".join(formatted_sections)
    
    async def _make_api_call(self, prompt: str) -> str:
        """Make async API call to Gemini"""
        try:
            # Use asyncio to run the sync API call in a thread
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._sync_api_call, prompt)
            return response
        except Exception as e:
            raise Exception(f"API call failed: {e}")
    
    def _sync_api_call(self, prompt: str) -> str:
        """Synchronous API call to Gemini"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate Gemini response"""
        try:
            # Clean the response text
            cleaned_response = response_text.strip()
            
            # Try to parse as JSON
            decision = json.loads(cleaned_response)
            
            # Validate required fields
            required_fields = ['decisions', 'reasoning', 'confidence', 'scores']
            for field in required_fields:
                if field not in decision:
                    print(f"Warning: Missing required field '{field}' in LLM response")
                    decision[field] = self._get_default_value(field)
            
            # Ensure scores are in valid range
            if 'scores' in decision:
                for score_name, score_value in decision['scores'].items():
                    if not isinstance(score_value, (int, float)) or not (0 <= score_value <= 1):
                        decision['scores'][score_name] = 0.5
            
            # Ensure confidence is valid
            if 'confidence' in decision:
                if not isinstance(decision['confidence'], (int, float)) or not (0 <= decision['confidence'] <= 1):
                    decision['confidence'] = 0.8
            
            return decision
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Response text: {response_text}")
            return self._fallback_decision({})
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return self._fallback_decision({})
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'decisions': [],
            'reasoning': 'Unable to parse agent reasoning',
            'confidence': 0.5,
            'scores': {'comfort': 0.5, 'energy': 0.5, 'reliability': 0.5, 'security': 0.5},
            'emergency_level': 0
        }
        return defaults.get(field, None)
    
    def _fallback_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback decision when API fails"""
        return {
            "decisions": [
                {
                    "device_id": "system",
                    "action": "maintain_current_state",
                    "parameters": {},
                    "priority": 0.5
                }
            ],
            "reasoning": "Fallback decision due to LLM API failure. Maintaining current device states for safety.",
            "confidence": 0.3,
            "scores": {
                "comfort": 0.5,
                "energy": 0.5,
                "reliability": 0.8,
                "security": 0.7
            },
            "emergency_level": 0
        }


# Global instance
gemini_client = None

def get_gemini_client() -> GeminiLLMClient:
    """Get or create global Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        try:
            gemini_client = GeminiLLMClient()
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            print("LLM agents will use fallback decision logic")
            gemini_client = None
    return gemini_client

def is_gemini_available() -> bool:
    """Check if Gemini API is available"""
    return os.getenv('GOOGLE_API_KEY') is not None
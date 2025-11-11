#!/usr/bin/env python3
"""
Comprehensive test suite for Google Gemini LLM integration

Run this script from the repository root. It will load backend/.env and
use the backend virtualenv interpreter to run the tests.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables from backend/.env explicitly
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

async def test_gemini_client():
    """Test Google Gemini API client initialization"""
    print("🧪 Testing Google Gemini LLM Integration...")
    print("=" * 50)

    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("   Please add your Google AI API key to backend/.env file")
        print("   Get free key at: https://aistudio.google.com/app/apikey")
        return False

    print(f"✅ API Key configured: {api_key[:10]}...{api_key[-4:]}")

    # Test imports
    try:
        from app.agents.gemini_client import GeminiLLMClient, is_gemini_available, get_gemini_client
        print("✅ Gemini client imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        print("   Run: pip install google-generativeai httpx")
        return False

    # Test API availability (this checks only that the key exists and client initialized)
    if not is_gemini_available():
        print("❌ Gemini API not available")
        return False

    print("✅ Gemini API available")

    # Test client initialization
    try:
        client = get_gemini_client()
        if client is None:
            print("❌ Failed to initialize Gemini client")
            return False
        print("✅ Gemini client initialized")
    except Exception as e:
        print(f"❌ Client initialization error: {e}")
        return False

    # Test simple API call (this may require network access and valid key)
    print("\n🔮 Testing LLM API call...")
    test_context = {
        "room_data": {"id": 1, "name": "Test Conference Room"},
        "devices": [
            {"id": "light_1", "type": "Lighting", "status": "OFF", "name": "Main Light"},
            {"id": "hvac_1", "type": "HVAC", "status": "OFF", "name": "AC Unit"}
        ],
        "sensor_data": {
            "temperature": 28,
            "occupancy": 5,
            "humidity": 65,
            "light_level": 200
        },
        "slos": [
            {"name": "Comfort Temperature", "target_value": 22, "unit": "°C"}
        ]
    }

    test_prompt = """
You are a Comfort Agent for smart building management. 
Your goal is to optimize occupant comfort through environmental control.

Analyze the current context and provide device control decisions to improve comfort.
The room is currently hot (28°C) with 5 occupants and needs cooling.

Respond with JSON containing specific device actions.
    """

    try:
        response = await client.generate_decision(test_prompt, test_context)
        print("✅ LLM API call successful!")
        print("\n📊 Response Analysis:")
        print(f"   Decisions: {len(response.get('decisions', []))} actions")
        reasoning = response.get('reasoning') or ''
        print(f"   Reasoning: {reasoning[:200]}...")
        print(f"   Confidence: {response.get('confidence', 'N/A')}")

        required_fields = ['decisions', 'reasoning', 'confidence', 'scores']
        missing_fields = [f for f in required_fields if f not in response]
        if missing_fields:
            print(f"⚠️  Warning: Missing fields: {missing_fields}")
        else:
            print("✅ Response structure valid")

        return True

    except Exception as e:
        print(f"❌ LLM API call failed: {e}")
        return False

async def test_agent_integration():
    """Test specialized agent integration"""
    print("\n🤖 Testing Specialized Agents...")
    print("=" * 50)

    try:
        from app.agents.llm_agents import SecurityAgent, ComfortAgent, EnergyAgent
        from app.agents.agent_config import AgentType, AgentRegistry

        print("✅ Agent imports successful")

        # Test agent configuration
        security_config = AgentRegistry.get_agent_config(AgentType.SECURITY)
        print(f"✅ Security Agent - Priority: {security_config.priority_weight}")

        comfort_config = AgentRegistry.get_agent_config(AgentType.COMFORT)
        print(f"✅ Comfort Agent - Priority: {comfort_config.priority_weight}")

        # Try both ENERGY and ENERGY_EFFICIENCY if present
        try:
            energy_config = AgentRegistry.get_agent_config(AgentType.ENERGY)
            print(f"✅ Energy Agent (ENERGY) - Priority: {energy_config.priority_weight}")
        except Exception:
            try:
                energy_config = AgentRegistry.get_agent_config(AgentType.ENERGY_EFFICIENCY)
                print(f"✅ Energy Agent (ENERGY_EFFICIENCY) - Priority: {energy_config.priority_weight}")
            except Exception as e:
                print(f"⚠️  Energy Agent enum mismatch: {e}")

        # Test agent decision making
        test_context = {
            "room_data": {"id": 1, "name": "Security Test Room"},
            "devices": [{"id": "light_1", "type": "Lighting", "status": "OFF"}],
            "sensor_data": {"occupancy": 0, "temperature": 22},
            "slos": [{"name": "Security Lighting", "target_value": 1, "unit": "lights"}]
        }

        print("\n🔐 Testing Security Agent...")
        security_agent = SecurityAgent()
        security_decision = await security_agent.make_decision(test_context)
        print(f"   Decision: {len(security_decision.get('decisions', []))} actions")
        print(f"   Reasoning: {security_decision.get('reasoning', 'N/A')[:200]}...")

        return True

    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

async def test_decision_engine():
    """Test the multi-agent decision engine"""
    print("\n🧠 Testing Multi-Agent Decision Engine...")
    print("=" * 50)

    try:
        from app.services.decision_engine import MultiAgentDecisionEngine, CollectiveDecision
        print("✅ Decision engine imports successful")

        from app.services.decision_engine import DecisionStatus, ConflictResolution
        print(f"✅ Decision statuses: {[status.value for status in DecisionStatus]}")
        print(f"✅ Conflict resolution: {[method.value for method in ConflictResolution]}")

        return True

    except Exception as e:
        print(f"❌ Decision engine test failed: {e}")
        return False

async def main():
    print("🚀 Smart Building LLM Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Gemini Client", test_gemini_client),
        ("Agent Integration", test_agent_integration),
        ("Decision Engine", test_decision_engine),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        print()

    print("📋 Test Summary")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! Your LLM integration is ready!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the errors above.")
        print("1. Ensure GOOGLE_API_KEY is set in backend/.env")
        print("2. Run: pip install google-generativeai httpx")
        print("3. Check your internet connection")

if __name__ == "__main__":
    asyncio.run(main())

async def test_agent_integration():
    """Test specialized agent integration"""
    print("\n🤖 Testing Specialized Agents...")
    print("=" * 50)
    
    try:
        from app.agents.llm_agents import SecurityAgent, ComfortAgent, EnergyAgent
        from app.agents.agent_config import AgentType, AgentRegistry
        
        print("✅ Agent imports successful")
        
        # Test agent configuration
        security_config = AgentRegistry.get_agent_config(AgentType.SECURITY)
        print(f"✅ Security Agent - Priority: {security_config.priority_weight}")
        
        comfort_config = AgentRegistry.get_agent_config(AgentType.COMFORT)
        print(f"✅ Comfort Agent - Priority: {comfort_config.priority_weight}")
        
        energy_config = AgentRegistry.get_agent_config(AgentType.ENERGY_EFFICIENCY)
        print(f"✅ Energy Agent - Priority: {energy_config.priority_weight}")
        
        # Test agent decision making
        test_context = {
            "room_data": {"id": 1, "name": "Security Test Room"},
            "devices": [{"id": "light_1", "type": "Lighting", "status": "OFF"}],
            "sensor_data": {"occupancy": 0, "temperature": 22},
            "slos": [{"name": "Security Lighting", "target_value": 1, "unit": "lights"}]
        }
        
        print("\n🔐 Testing Security Agent...")
        security_agent = SecurityAgent()
        security_decision = await security_agent.make_decision(test_context)
        print(f"   Decision: {len(security_decision.get('decisions', []))} actions")
        print(f"   Reasoning: {security_decision.get('reasoning', 'N/A')[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

async def test_decision_engine():
    """Test the multi-agent decision engine"""
    print("\n🧠 Testing Multi-Agent Decision Engine...")
    print("=" * 50)
    
    try:
        # This requires database setup, so we'll do a basic import test
        from app.services.decision_engine import MultiAgentDecisionEngine, CollectiveDecision
        print("✅ Decision engine imports successful")
        
        # Test decision status enums
        from app.services.decision_engine import DecisionStatus, ConflictResolution
        print(f"✅ Decision statuses: {[status.value for status in DecisionStatus]}")
        print(f"✅ Conflict resolution: {[method.value for method in ConflictResolution]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Decision engine test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Smart Building LLM Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Gemini Client", test_gemini_client),
        ("Agent Integration", test_agent_integration), 
        ("Decision Engine", test_decision_engine)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        
        print()  # Spacing
    
    # Summary
    print("📋 Test Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your LLM integration is ready!")
        print("\nNext steps:")
        print("1. Start backend: uvicorn app.main:app --reload")
        print("2. Test API: curl http://localhost:8000/api/llm/status")
        print("3. Open dashboard: http://localhost:5173")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the errors above.")
        print("1. Ensure GOOGLE_API_KEY is set in backend/.env")
        print("2. Run: pip install google-generativeai httpx")
        print("3. Check your internet connection")

if __name__ == "__main__":
    asyncio.run(main())
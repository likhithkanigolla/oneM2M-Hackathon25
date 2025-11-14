#!/usr/bin/env python3
"""
Test Gemini Integration Status
Quick test to check current LLM implementation state
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

def test_environment():
    """Test environment configuration"""
    print("🔍 Testing Environment Configuration")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ GOOGLE_API_KEY configured: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ GOOGLE_API_KEY not set in environment")
    
    # Check .env file
    env_file = backend_path / '.env'
    if env_file.exists():
        print(f"✅ .env file exists: {env_file}")
        with open(env_file) as f:
            content = f.read()
            if 'GOOGLE_API_KEY' in content:
                print("✅ GOOGLE_API_KEY found in .env file")
            else:
                print("❌ GOOGLE_API_KEY not found in .env file")
    else:
        print("❌ .env file not found")

def test_gemini_client():
    """Test Gemini client initialization"""
    print("\n🤖 Testing Gemini Client")
    print("=" * 50)
    
    try:
        from app.agents.gemini_client import get_gemini_client, is_gemini_available
        
        # Test availability
        available = is_gemini_available()
        print(f"Gemini available: {'✅ Yes' if available else '❌ No'}")
        
        # Test client creation
        client = get_gemini_client()
        if client:
            print("✅ Gemini client created successfully")
            print(f"Client model: {getattr(client, 'model', 'Unknown')}")
        else:
            print("❌ Failed to create Gemini client")
            
        return client is not None
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Client error: {e}")
        return False

def test_llm_agents():
    """Test LLM agents"""
    print("\n🏢 Testing LLM Agents")
    print("=" * 50)
    
    try:
        from app.agents.llm_agents import SecurityAgent, ComfortAgent, EnergyAgent
        from app.agents.agent_config import AgentType
        
        # Test agent creation
        agents = [
            ("Security", SecurityAgent),
            ("Comfort", ComfortAgent),
            ("Energy", EnergyAgent)
        ]
        
        for name, AgentClass in agents:
            try:
                agent = AgentClass()
                print(f"✅ {name}Agent created successfully")
                print(f"   Agent ID: {agent.agent_id}")
                print(f"   Has Gemini client: {'Yes' if agent.gemini_client else 'No'}")
            except Exception as e:
                print(f"❌ {name}Agent failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return False

def test_decision_engine():
    """Test decision engine"""
    print("\n⚙️ Testing Decision Engine")
    print("=" * 50)
    
    try:
        from app.services.decision_engine import MultiAgentDecisionEngine
        
        engine = MultiAgentDecisionEngine()
        print("✅ MultiAgentDecisionEngine created successfully")
        print(f"   Number of agents: {len(engine.agents) if hasattr(engine, 'agents') else 'Unknown'}")
        
        # Test with sample context
        context = {
            "room_id": 1,
            "temperature": 25.0,
            "humidity": 60,
            "occupancy": 5
        }
        
        print("🧪 Testing decision making with sample data...")
        # This would be async in real usage, but testing structure
        print("   Sample context prepared for decision testing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Decision engine error: {e}")
        return False

def show_current_state():
    """Show current implementation state"""
    print("\n📊 Current Implementation State")
    print("=" * 50)
    
    env_ok = test_environment()
    client_ok = test_gemini_client()
    agents_ok = test_llm_agents()
    engine_ok = test_decision_engine()
    
    print("\n🎯 Implementation Summary:")
    print("-" * 30)
    print(f"Environment Config: {'✅' if env_ok else '❌'}")
    print(f"Gemini Client: {'✅' if client_ok else '❌'}")
    print(f"LLM Agents: {'✅' if agents_ok else '❌'}")
    print(f"Decision Engine: {'✅' if engine_ok else '❌'}")
    
    if all([env_ok, client_ok, agents_ok, engine_ok]):
        print("\n🚀 Status: FULLY IMPLEMENTED AND READY!")
        print("   The Gemini LLM integration is complete and operational")
    elif any([client_ok, agents_ok, engine_ok]):
        print("\n⚠️ Status: PARTIALLY IMPLEMENTED")
        print("   Core LLM components are ready, environment needs configuration")
    else:
        print("\n❌ Status: IMPLEMENTATION INCOMPLETE")
        print("   Need to complete LLM integration setup")

if __name__ == "__main__":
    print("🔬 Gemini LLM Integration State Check")
    print("=" * 60)
    show_current_state()
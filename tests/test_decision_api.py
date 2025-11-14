#!/usr/bin/env python3
"""
Simple Decision Management Integration Test

Tests the complete decision workflow using the backend API endpoints.
Run this with the backend server running to validate the complete platform.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
import aiohttp


class SimpleDecisionTest:
    """Simple test suite using HTTP API calls"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    async def run_all_tests(self):
        """Run complete test suite via API calls"""
        
        print("🚀 Smart Building Decision Management API Test")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            
            # Test 1: Health check
            await self.test_health_check(session)
            
            # Test 2: Initialize SLOs
            await self.test_initialize_slos(session)
            
            # Test 3: LLM status
            await self.test_llm_status(session)
            
            # Test 4: SLO evaluation for a room
            await self.test_slo_evaluation(session)
            
            # Test 5: Decision coordination
            await self.test_decision_coordination(session)
            
            # Generate report
            return self.generate_report()
    
    async def test_health_check(self, session):
        """Test system health"""
        print("\n🏥 Testing System Health...")
        
        try:
            async with session.get(f"{self.base_url}/api/decisions/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ System status: {data.get('status', 'unknown')}")
                    
                    services = data.get('services', {})
                    for service, status in services.items():
                        emoji = "✅" if status == "operational" else "⚠️"
                        print(f"    {emoji} {service}: {status}")
                    
                    self.test_results['health_check'] = {'success': True, 'services': services}
                else:
                    print(f"  ❌ Health check failed with status {response.status}")
                    self.test_results['health_check'] = {'success': False, 'status': response.status}
        
        except Exception as e:
            print(f"  ❌ Health check failed: {e}")
            self.test_results['health_check'] = {'success': False, 'error': str(e)}
    
    async def test_initialize_slos(self, session):
        """Test SLO initialization"""
        print("\n📊 Testing SLO Initialization...")
        
        try:
            async with session.post(f"{self.base_url}/api/decisions/slos/initialize") as response:
                if response.status in [200, 400]:  # 400 if already exists
                    data = await response.json()
                    message = data.get('message', 'Unknown response')
                    print(f"  ✅ {message}")
                    
                    if 'created_slos' in data:
                        print(f"    Created {data['created_slos']} new SLOs")
                    if 'existing_slos' in data:
                        print(f"    Found {data['existing_slos']} existing SLOs")
                    
                    self.test_results['slo_init'] = {'success': True, 'response': data}
                else:
                    print(f"  ❌ SLO initialization failed with status {response.status}")
                    self.test_results['slo_init'] = {'success': False, 'status': response.status}
        
        except Exception as e:
            print(f"  ❌ SLO initialization failed: {e}")
            self.test_results['slo_init'] = {'success': False, 'error': str(e)}
    
    async def test_llm_status(self, session):
        """Test LLM integration status"""
        print("\n🧠 Testing LLM Status...")
        
        try:
            async with session.get(f"{self.base_url}/api/llm/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get('status', 'unknown')
                    model = data.get('model', 'unknown')
                    
                    print(f"  ✅ LLM status: {status}")
                    print(f"    Model: {model}")
                    
                    if 'api_key_configured' in data:
                        api_configured = data['api_key_configured']
                        emoji = "✅" if api_configured else "⚠️"
                        print(f"    {emoji} API Key: {'Configured' if api_configured else 'Missing'}")
                    
                    self.test_results['llm_status'] = {'success': True, 'status': status, 'model': model}
                else:
                    print(f"  ❌ LLM status check failed with status {response.status}")
                    self.test_results['llm_status'] = {'success': False, 'status': response.status}
        
        except Exception as e:
            print(f"  ❌ LLM status check failed: {e}")
            self.test_results['llm_status'] = {'success': False, 'error': str(e)}
    
    async def test_slo_evaluation(self, session):
        """Test SLO evaluation for a room"""
        print("\n📋 Testing SLO Evaluation...")
        
        try:
            room_id = 1  # Test with room 1
            async with session.post(f"{self.base_url}/api/decisions/slos/evaluate/{room_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    compliance = data.get('overall_compliance', 0.0)
                    violations = data.get('violations', [])
                    scores = data.get('category_scores', {})
                    
                    print(f"  ✅ Room {room_id} evaluation completed")
                    print(f"    Overall compliance: {compliance:.1%}")
                    print(f"    Violations: {len(violations)}")
                    print(f"    Category scores:")
                    
                    for category, score in scores.items():
                        emoji = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🔴"
                        print(f"      {emoji} {category}: {score:.1%}")
                    
                    self.test_results['slo_evaluation'] = {
                        'success': True, 
                        'compliance': compliance,
                        'violations_count': len(violations),
                        'scores': scores
                    }
                else:
                    print(f"  ❌ SLO evaluation failed with status {response.status}")
                    text = await response.text()
                    print(f"    Error: {text}")
                    self.test_results['slo_evaluation'] = {'success': False, 'status': response.status}
        
        except Exception as e:
            print(f"  ❌ SLO evaluation failed: {e}")
            self.test_results['slo_evaluation'] = {'success': False, 'error': str(e)}
    
    async def test_decision_coordination(self, session):
        """Test decision coordination"""
        print("\n🤖 Testing Decision Coordination...")
        
        try:
            # Prepare coordination request
            request_data = {
                "room_id": 1,
                "resolution_strategies": ["priority_weighted", "safety_first", "energy_balance"]
            }
            
            start_time = time.time()
            async with session.post(f"{self.base_url}/api/decisions/coordinate", json=request_data) as response:
                coordination_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    total_plans = data.get('total_plans', 0)
                    plans = data.get('plans', [])
                    
                    print(f"  ✅ Coordination completed in {coordination_time:.0f}ms")
                    print(f"    Generated {total_plans} decision plans")
                    
                    if plans:
                        best_plan = plans[0]
                        score = best_plan.get('score', 0.0)
                        confidence = best_plan.get('confidence', 0.0)
                        actions = len(best_plan.get('actions', []))
                        
                        print(f"    Best plan: Score={score:.2f}, Confidence={confidence:.2f}, Actions={actions}")
                        
                        # Show execution recommendation
                        metadata = best_plan.get('metadata', {})
                        recommendation = metadata.get('execution_recommendation', 'MANUAL')
                        print(f"    Execution recommendation: {recommendation}")
                    
                    self.test_results['coordination'] = {
                        'success': True,
                        'coordination_time_ms': coordination_time,
                        'plans_generated': total_plans,
                        'best_score': plans[0].get('score', 0.0) if plans else 0.0
                    }
                    
                else:
                    print(f"  ❌ Decision coordination failed with status {response.status}")
                    text = await response.text()
                    print(f"    Error: {text}")
                    self.test_results['coordination'] = {'success': False, 'status': response.status}
        
        except Exception as e:
            print(f"  ❌ Decision coordination failed: {e}")
            self.test_results['coordination'] = {'success': False, 'error': str(e)}
    
    def generate_report(self):
        """Generate test report"""
        
        successful_tests = sum(1 for result in self.test_results.values() 
                             if result.get('success', False))
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📋 DECISION SYSTEM API TEST REPORT")
        print("=" * 50)
        
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"🎯 Success rate: {success_rate:.1f}%")
        
        print("\n📊 Test Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"  {test_name}: {status}")
            
            if not result.get('success', False):
                error = result.get('error', result.get('status', 'Unknown error'))
                print(f"    Error: {error}")
        
        # System assessment
        print(f"\n🚀 SYSTEM READINESS:")
        if success_rate >= 80:
            print("🟢 READY FOR DEMO - Core functionality operational")
            readiness = "READY"
        elif success_rate >= 60:
            print("🟡 PARTIALLY READY - Some issues detected")
            readiness = "PARTIAL"
        else:
            print("🔴 NOT READY - Critical issues need resolution")
            readiness = "NOT_READY"
        
        return {
            'readiness': readiness,
            'success_rate': success_rate,
            'results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main test execution"""
    
    print("🏢 Smart Building Decision Management Platform")
    print("🔍 API Integration Test Suite")
    print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/") as response:
                if response.status == 200:
                    print("✅ Backend server detected on http://localhost:8000")
                else:
                    print("❌ Backend server not responding correctly")
                    return
    except Exception as e:
        print("❌ Cannot connect to backend server")
        print("   Please start the backend server first:")
        print("   cd backend && uvicorn app.main:app --reload")
        return
    
    # Run tests
    test_suite = SimpleDecisionTest()
    results = await test_suite.run_all_tests()
    
    # Save results
    filename = f"api_test_results_{datetime.now().strftime('%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to {filename}")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        if results and results.get('readiness') == 'READY':
            print("\n🎉 PLATFORM READY FOR DEMONSTRATION!")
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(3)
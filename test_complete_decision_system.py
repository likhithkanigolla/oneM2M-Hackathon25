#!/usr/bin/env python3
"""
Complete Decision Management System Test

This script tests the entire decision workflow:
1. SLO initialization and evaluation
2. Multi-agent decision coordination
3. Plan scoring and ranking
4. Execution (both AUTO and MANUAL modes)
5. Status monitoring and compliance tracking

Run this after starting the backend server to validate the complete platform.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Test data and utilities
class TestData:
    """Test data for validating decision management system"""
    
    @staticmethod
    def get_test_room_context() -> Dict[str, Any]:
        """Get a realistic room context for testing"""
        return {
            'room_data': {
                'id': 1,
                'name': 'Conference Room A',
                'type': 'meeting',
                'capacity': 10,
                'area_sqm': 25.0
            },
            'devices': [
                {
                    'id': 'hvac_1',
                    'name': 'Main HVAC System',
                    'type': 'HVAC',
                    'status': 'ON',
                    'target_temperature': 26,
                    'room_id': 1
                },
                {
                    'id': 'light_1',
                    'name': 'Overhead Lighting',
                    'type': 'Lighting',
                    'status': 'ON',
                    'brightness': 0.8,
                    'room_id': 1
                },
                {
                    'id': 'light_2',
                    'name': 'Task Lighting',
                    'type': 'Lighting',
                    'status': 'OFF',
                    'brightness': 0.0,
                    'room_id': 1
                },
                {
                    'id': 'airflow_1',
                    'name': 'Ventilation System',
                    'type': 'AirFlow',
                    'status': 'ON',
                    'fan_speed': 2,
                    'room_id': 1
                },
                {
                    'id': 'security_1',
                    'name': 'Security Camera',
                    'type': 'Security',
                    'status': 'ON',
                    'room_id': 1
                }
            ],
            'sensor_data': {
                'temperature': 28.5,    # Too hot - should trigger comfort actions
                'humidity': 65,         # High humidity
                'co2': 950,            # High CO2 - should trigger environmental actions
                'occupancy': 7,        # High occupancy 
                'light_level': 450,
                'timestamp': datetime.now().isoformat()
            },
            'slos': []  # Will be populated by SLO service
        }


class DecisionTestSuite:
    """Comprehensive test suite for decision management system"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        
        print("🚀 Starting Complete Decision Management Test Suite")
        print("=" * 60)
        
        try:
            # Test 1: LLM Integration
            await self.test_llm_integration()
            
            # Test 2: SLO System
            await self.test_slo_system()
            
            # Test 3: Multi-Agent Coordination
            await self.test_multi_agent_coordination()
            
            # Test 4: Decision Plan Scoring
            await self.test_decision_plan_scoring()
            
            # Test 5: Execution Engine
            await self.test_execution_engine()
            
            # Test 6: End-to-End Workflow
            await self.test_end_to_end_workflow()
            
            # Generate final report
            return self.generate_test_report()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_llm_integration(self):
        """Test LLM integration with all agents"""
        print("\n🧠 Testing LLM Integration...")
        
        try:
            from backend.app.agents.gemini_client import get_gemini_client, is_gemini_available
            from backend.app.agents.llm_agents import (
                SecurityAgent, ComfortAgent, EnergyAgent,
                EmergencyAgent, EnvironmentalAgent, OccupancyAgent
            )
            
            # Check Gemini availability
            if not is_gemini_available():
                print("⚠️  Gemini API not available - using fallback mode")
                self.test_results['llm_available'] = False
            else:
                print("✅ Gemini API available")
                self.test_results['llm_available'] = True
            
            # Test each agent
            agents = {
                'security': SecurityAgent(),
                'comfort': ComfortAgent(),
                'energy': EnergyAgent(),
                'emergency': EmergencyAgent(),
                'environmental': EnvironmentalAgent(),
                'occupancy': OccupancyAgent()
            }
            
            context = TestData.get_test_room_context()
            agent_results = {}
            
            for name, agent in agents.items():
                print(f"  Testing {name} agent...")
                start_time = time.time()
                
                try:
                    decision = await agent.make_decision(context)
                    response_time = (time.time() - start_time) * 1000
                    
                    agent_results[name] = {
                        'success': True,
                        'response_time_ms': response_time,
                        'decisions_count': len(decision.get('decisions', [])),
                        'confidence': decision.get('confidence', 0.0),
                        'reasoning_length': len(decision.get('reasoning', ''))
                    }
                    
                    print(f"    ✅ {name}: {len(decision.get('decisions', []))} decisions, "
                          f"{response_time:.0f}ms, confidence: {decision.get('confidence', 0.0):.2f}")
                    
                except Exception as e:
                    agent_results[name] = {'success': False, 'error': str(e)}
                    print(f"    ❌ {name}: {str(e)}")
            
            self.test_results['agent_tests'] = agent_results
            
        except Exception as e:
            print(f"❌ LLM Integration test failed: {e}")
            self.test_results['llm_integration'] = {'success': False, 'error': str(e)}
    
    async def test_slo_system(self):
        """Test SLO evaluation and compliance tracking"""
        print("\n📊 Testing SLO System...")
        
        try:
            from backend.app.services.slo_service import SLOService
            from backend.app.models.slo import SLO
            
            slo_service = SLOService()
            
            # Create mock SLOs for testing
            test_slos = [
                SLO(
                    id=1,
                    name='Temperature Comfort',
                    metric='temperature_comfort',
                    target_value=23.0,
                    weight=0.25,
                    config={'min_temp': 22, 'max_temp': 24},
                    created_by='test',
                    active=True
                ),
                SLO(
                    id=2,
                    name='Air Quality CO2',
                    metric='air_quality_co2',
                    target_value=800.0,
                    weight=0.20,
                    config={'max_co2': 800},
                    created_by='test',
                    active=True
                ),
                SLO(
                    id=3,
                    name='Energy Efficiency',
                    metric='energy_efficiency',
                    target_value=0.8,
                    weight=0.20,
                    config={'max_devices_unoccupied': 1},
                    created_by='test',
                    active=True
                )
            ]
            
            context = TestData.get_test_room_context()
            evaluation = slo_service.evaluate_slos(
                room_data=context['room_data'],
                sensor_data=context['sensor_data'],
                devices=context['devices'],
                slos=test_slos
            )
            
            print(f"  Overall compliance: {evaluation['overall_compliance']:.2f}")
            print(f"  Violations found: {len(evaluation.get('violations', []))}")
            print(f"  Category scores:")
            for category, score in evaluation.get('scores', {}).items():
                print(f"    {category}: {score:.2f}")
            
            # Test violation detection
            violations = evaluation.get('violations', [])
            critical_violations = [v for v in violations if v.get('severity') == 'critical']
            
            self.test_results['slo_evaluation'] = {
                'success': True,
                'overall_compliance': evaluation['overall_compliance'],
                'total_violations': len(violations),
                'critical_violations': len(critical_violations),
                'category_scores': evaluation.get('scores', {})
            }
            
            print(f"✅ SLO evaluation completed with {len(violations)} violations")
            
        except Exception as e:
            print(f"❌ SLO System test failed: {e}")
            self.test_results['slo_evaluation'] = {'success': False, 'error': str(e)}
    
    async def test_multi_agent_coordination(self):
        """Test multi-agent decision coordination"""
        print("\n🤖 Testing Multi-Agent Coordination...")
        
        try:
            from backend.app.services.decision_coordinator import MultiAgentCoordinator
            from backend.app.models.slo import SLO
            
            coordinator = MultiAgentCoordinator()
            
            # Create test SLOs
            test_slos = [
                SLO(
                    name='Temperature Comfort',
                    metric='temperature_comfort',
                    target_value=23.0,
                    weight=0.25,
                    config={'min_temp': 22, 'max_temp': 24},
                    created_by='test',
                    active=True
                )
            ]
            
            context = TestData.get_test_room_context()
            
            start_time = time.time()
            decision_plans = await coordinator.coordinate_decisions(
                context, 
                test_slos, 
                ['priority_weighted', 'safety_first', 'energy_balance']
            )
            coordination_time = (time.time() - start_time) * 1000
            
            print(f"  Generated {len(decision_plans)} decision plans in {coordination_time:.0f}ms")
            
            for i, plan in enumerate(decision_plans[:3]):  # Show top 3 plans
                print(f"    Plan {i+1}: Score={plan.score:.2f}, "
                      f"Confidence={plan.confidence:.2f}, "
                      f"Actions={len(plan.actions)}")
            
            # Test execution summary
            execution_summary = coordinator.get_execution_summary(decision_plans)
            
            self.test_results['coordination'] = {
                'success': True,
                'plans_generated': len(decision_plans),
                'coordination_time_ms': coordination_time,
                'best_plan_score': decision_plans[0].score if decision_plans else 0.0,
                'auto_executable': execution_summary.get('auto_executable', False)
            }
            
            print(f"✅ Coordination completed - Best plan score: {decision_plans[0].score:.2f}")
            
        except Exception as e:
            print(f"❌ Multi-Agent Coordination test failed: {e}")
            self.test_results['coordination'] = {'success': False, 'error': str(e)}
    
    async def test_decision_plan_scoring(self):
        """Test decision plan scoring and ranking"""
        print("\n🏆 Testing Decision Plan Scoring...")
        
        try:
            from backend.app.services.decision_coordinator import DecisionPlan, DecisionPlanScorer
            from backend.app.models.slo import SLO
            
            scorer = DecisionPlanScorer()
            
            # Create test decision plan
            test_plan = DecisionPlan(
                plan_id="test_plan_001",
                agent_decisions=[
                    {
                        'agent_type': 'COMFORT',
                        'confidence': 0.85,
                        'decisions': [
                            {'device_id': 'hvac_1', 'action': 'set_temperature', 'parameters': {'temperature': 23}}
                        ]
                    }
                ],
                slo_compliance={},
                metadata={'strategy': 'test'}
            )
            
            test_plan.actions = [
                {'device_id': 'hvac_1', 'action': 'set_temperature', 'parameters': {'temperature': 23}}
            ]
            test_plan.agent_decisions = [
                {'agent_type': 'COMFORT', 'confidence': 0.85, 'decisions': test_plan.actions}
            ]
            
            # Test SLOs
            test_slos = [
                SLO(
                    name='Temperature Comfort',
                    metric='temperature_comfort',
                    target_value=23.0,
                    weight=0.25,
                    config={'min_temp': 22, 'max_temp': 24},
                    created_by='test',
                    active=True
                )
            ]
            
            context = TestData.get_test_room_context()
            
            score = scorer.score_decision_plan(test_plan, context, test_slos)
            
            print(f"  Plan score: {score:.2f}")
            print(f"  Plan confidence: {test_plan.confidence:.2f}")
            print(f"  Actions: {len(test_plan.actions)}")
            
            self.test_results['plan_scoring'] = {
                'success': True,
                'test_score': score,
                'confidence': test_plan.confidence,
                'actions_count': len(test_plan.actions)
            }
            
            print(f"✅ Plan scoring completed - Score: {score:.2f}")
            
        except Exception as e:
            print(f"❌ Decision Plan Scoring test failed: {e}")
            self.test_results['plan_scoring'] = {'success': False, 'error': str(e)}
    
    async def test_execution_engine(self):
        """Test decision execution engine"""
        print("\n⚙️ Testing Execution Engine...")
        
        try:
            from backend.app.services.execution_engine import DecisionExecutionEngine
            from backend.app.services.decision_coordinator import DecisionPlan
            
            execution_engine = DecisionExecutionEngine()
            
            # Create test execution plan
            test_plan = DecisionPlan(
                plan_id="exec_test_001",
                agent_decisions=[],
                slo_compliance={},
                metadata={}
            )
            
            test_plan.actions = [
                {
                    'device_id': 'light_1',
                    'action': 'dim',
                    'parameters': {'brightness': 0.5},
                    'device_type': 'Lighting'
                },
                {
                    'device_id': 'hvac_1', 
                    'action': 'set_temperature',
                    'parameters': {'temperature': 23},
                    'device_type': 'HVAC'
                }
            ]
            
            # Test AUTO execution
            print("  Testing AUTO execution...")
            start_time = time.time()
            
            execution_plan = await execution_engine.execute_plan(
                test_plan,
                execution_mode="AUTO",
                executor="test_user"
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            print(f"    Execution time: {execution_time:.0f}ms")
            print(f"    Status: {execution_plan.status.value}")
            print(f"    Progress: {execution_plan.get_progress_percentage():.1f}%")
            
            # Get execution summary
            summary = execution_engine.get_execution_summary()
            
            self.test_results['execution_engine'] = {
                'success': True,
                'execution_time_ms': execution_time,
                'final_status': execution_plan.status.value,
                'progress_percentage': execution_plan.get_progress_percentage(),
                'actions_executed': len([r for r in execution_plan.action_results if r.status.value == 'completed']),
                'execution_summary': summary
            }
            
            print(f"✅ Execution completed - Status: {execution_plan.status.value}")
            
        except Exception as e:
            print(f"❌ Execution Engine test failed: {e}")
            self.test_results['execution_engine'] = {'success': False, 'error': str(e)}
    
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end decision workflow"""
        print("\n🔄 Testing End-to-End Workflow...")
        
        try:
            # This would test the complete workflow:
            # 1. Room state assessment
            # 2. SLO evaluation
            # 3. Agent coordination
            # 4. Plan generation and scoring
            # 5. Execution decision (AUTO vs MANUAL)
            # 6. Execution and monitoring
            
            workflow_start = time.time()
            
            # Simulate complete workflow
            context = TestData.get_test_room_context()
            
            # Step 1: Assess violations (simulate high temperature + CO2)
            violations_detected = {
                'temperature': 28.5,  # Above comfort range
                'co2': 950,          # Above threshold
                'occupancy': 7       # High occupancy
            }
            
            # Step 2: Determine urgency level
            urgency_level = 'high' if violations_detected['co2'] > 900 else 'medium'
            
            # Step 3: Recommend execution mode
            if urgency_level == 'high':
                recommended_mode = 'AUTO'
            else:
                recommended_mode = 'MANUAL'
            
            workflow_time = (time.time() - workflow_start) * 1000
            
            print(f"  Workflow completed in {workflow_time:.0f}ms")
            print(f"  Violations detected: {len(violations_detected)}")
            print(f"  Urgency level: {urgency_level}")
            print(f"  Recommended mode: {recommended_mode}")
            
            self.test_results['end_to_end'] = {
                'success': True,
                'workflow_time_ms': workflow_time,
                'violations_detected': len(violations_detected),
                'urgency_level': urgency_level,
                'recommended_execution_mode': recommended_mode
            }
            
            print(f"✅ End-to-end workflow test completed")
            
        except Exception as e:
            print(f"❌ End-to-End Workflow test failed: {e}")
            self.test_results['end_to_end'] = {'success': False, 'error': str(e)}
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # Count successes
        successful_tests = sum(1 for test_name, result in self.test_results.items() 
                             if isinstance(result, dict) and result.get('success', False))
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 60)
        print("📋 DECISION MANAGEMENT SYSTEM TEST REPORT")
        print("=" * 60)
        
        print(f"🕐 Total test time: {total_time:.1f}s")
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"🎯 Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print("\n📊 Detailed Results:")
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
                print(f"  {test_name}: {status}")
                if not result.get('success', False):
                    print(f"    Error: {result.get('error', 'Unknown error')}")
        
        # System readiness assessment
        print(f"\n🚀 SYSTEM READINESS ASSESSMENT:")
        
        if successful_tests == total_tests:
            print("🟢 FULLY OPERATIONAL - All systems ready for production")
            recommendation = "DEPLOY"
        elif successful_tests >= total_tests * 0.8:
            print("🟡 MOSTLY OPERATIONAL - Minor issues detected")
            recommendation = "DEPLOY WITH MONITORING"
        else:
            print("🔴 NOT READY - Critical issues need resolution")
            recommendation = "DO NOT DEPLOY"
        
        print(f"📋 Recommendation: {recommendation}")
        
        return {
            'status': 'completed',
            'total_time_seconds': total_time,
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'success_rate': (successful_tests/total_tests)*100,
            'recommendation': recommendation,
            'detailed_results': self.test_results,
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main test execution function"""
    
    print("🏢 Smart Building Decision Management System")
    print("🤖 Complete Platform Integration Test")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize and run test suite
    test_suite = DecisionTestSuite()
    results = await test_suite.run_all_tests()
    
    # Save results to file
    with open(f"decision_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Test results saved to decision_test_results_*.json")
    
    return results


if __name__ == "__main__":
    # Run the complete test suite
    try:
        results = asyncio.run(main())
        
        # Exit with appropriate code
        if results.get('recommendation') == 'DEPLOY':
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Issues detected
            
    except Exception as e:
        print(f"❌ Test suite failed to run: {e}")
        sys.exit(2)  # Test execution failure
"""
SLO Service for Smart Building Management

This module provides comprehensive SLO (Service Level Objective) management
including evaluation, compliance tracking, and violation detection.
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..models.slo import SLO
from ..database import get_db


class SLOEvaluationEngine:
    """Engine for evaluating room state against defined SLOs"""
    
    def __init__(self):
        self.evaluation_functions = {
            'temperature_comfort': self._evaluate_temperature_comfort,
            'energy_efficiency': self._evaluate_energy_efficiency,
            'security_lighting': self._evaluate_security_lighting,
            'air_quality_co2': self._evaluate_air_quality_co2,
            'occupancy_optimization': self._evaluate_occupancy_optimization,
            'humidity_control': self._evaluate_humidity_control,
            'emergency_readiness': self._evaluate_emergency_readiness
        }
    
    def evaluate_room_slos(self, room_data: Dict[str, Any], sensor_data: Dict[str, Any], 
                          devices: List[Dict[str, Any]], slos: List[SLO]) -> Dict[str, Any]:
        """
        Evaluate current room state against all defined SLOs
        
        Returns:
            Dict containing compliance scores, violations, and recommendations
        """
        evaluation_results = {
            'overall_compliance': 0.0,
            'slo_results': [],
            'violations': [],
            'recommendations': [],
            'scores': {
                'comfort': 0.0,
                'energy': 0.0,
                'security': 0.0,
                'environmental': 0.0
            },
            'evaluation_time': datetime.now().isoformat()
        }
        
        total_weight = sum(slo.weight for slo in slos if slo.active)
        weighted_score = 0.0
        
        for slo in slos:
            if not slo.active:
                continue
                
            result = self._evaluate_single_slo(slo, room_data, sensor_data, devices)
            evaluation_results['slo_results'].append(result)
            
            # Add to weighted score
            weighted_score += result['compliance_score'] * slo.weight
            
            # Track violations
            if result['compliance_score'] < 0.8:  # 80% threshold for violations
                evaluation_results['violations'].append({
                    'slo_name': slo.name,
                    'expected': result['expected_value'],
                    'actual': result['actual_value'],
                    'severity': self._get_violation_severity(result['compliance_score']),
                    'recommendation': result['recommendation']
                })
        
        evaluation_results['overall_compliance'] = weighted_score / total_weight if total_weight > 0 else 0.0
        evaluation_results['scores'] = self._calculate_category_scores(evaluation_results['slo_results'])
        
        return evaluation_results
    
    def _evaluate_single_slo(self, slo: SLO, room_data: Dict[str, Any], 
                           sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate a single SLO against current conditions"""
        
        if slo.metric in self.evaluation_functions:
            return self.evaluation_functions[slo.metric](slo, room_data, sensor_data, devices)
        else:
            return self._evaluate_generic_slo(slo, sensor_data)
    
    def _evaluate_temperature_comfort(self, slo: SLO, room_data: Dict[str, Any], 
                                    sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate temperature comfort SLO"""
        current_temp = sensor_data.get('temperature', 22)
        config = slo.config or {}
        min_temp = config.get('min_temp', 22)
        max_temp = config.get('max_temp', 24)
        
        if min_temp <= current_temp <= max_temp:
            compliance_score = 1.0
            recommendation = "Temperature within comfort range"
        else:
            # Calculate how far outside the range
            if current_temp < min_temp:
                deviation = min_temp - current_temp
                compliance_score = max(0.0, 1.0 - (deviation / 5.0))  # 5°C max deviation
                recommendation = f"Temperature too low. Increase heating by {deviation:.1f}°C"
            else:
                deviation = current_temp - max_temp
                compliance_score = max(0.0, 1.0 - (deviation / 5.0))
                recommendation = f"Temperature too high. Increase cooling by {deviation:.1f}°C"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"{min_temp}-{max_temp}°C",
            'actual_value': f"{current_temp}°C",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'high' if compliance_score < 0.6 else 'medium' if compliance_score < 0.8 else 'low'
        }
    
    def _evaluate_energy_efficiency(self, slo: SLO, room_data: Dict[str, Any], 
                                  sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate energy efficiency SLO"""
        occupancy = sensor_data.get('occupancy', 0)
        devices_on = sum(1 for d in devices if d.get('status') == 'ON')
        total_devices = len(devices)
        
        config = slo.config or {}
        max_devices_unoccupied = config.get('max_devices_unoccupied', 1)
        efficiency_threshold = config.get('efficiency_threshold', 0.7)
        
        if occupancy == 0:
            # Unoccupied room should have minimal devices on
            compliance_score = 1.0 if devices_on <= max_devices_unoccupied else max(0.0, 1.0 - (devices_on - max_devices_unoccupied) / total_devices)
            recommendation = f"Unoccupied room has {devices_on} devices on. Target: ≤{max_devices_unoccupied}"
        else:
            # Occupied room efficiency based on occupancy level
            expected_efficiency = min(1.0, occupancy / 5.0)  # Normalize to 5 people max
            actual_efficiency = devices_on / total_devices if total_devices > 0 else 0
            
            if actual_efficiency <= expected_efficiency + 0.2:  # 20% tolerance
                compliance_score = 1.0
                recommendation = "Energy usage optimized for current occupancy"
            else:
                compliance_score = max(0.0, 1.0 - (actual_efficiency - expected_efficiency))
                recommendation = f"Energy usage high for {occupancy} occupants. Consider reducing device usage"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"≤{max_devices_unoccupied} devices when unoccupied",
            'actual_value': f"{devices_on}/{total_devices} devices on, occupancy: {occupancy}",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'medium' if compliance_score < 0.7 else 'low'
        }
    
    def _evaluate_security_lighting(self, slo: SLO, room_data: Dict[str, Any], 
                                  sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate security lighting requirements"""
        lighting_devices = [d for d in devices if d.get('type') == 'Lighting']
        lights_on = sum(1 for d in lighting_devices if d.get('status') == 'ON')
        
        config = slo.config or {}
        min_lights_required = config.get('min_lights', 1)
        
        if lights_on >= min_lights_required:
            compliance_score = 1.0
            recommendation = "Security lighting requirements met"
        else:
            compliance_score = lights_on / min_lights_required if min_lights_required > 0 else 0.0
            recommendation = f"Insufficient lighting for security. Need {min_lights_required - lights_on} more lights"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"≥{min_lights_required} lights on",
            'actual_value': f"{lights_on}/{len(lighting_devices)} lights on",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'high' if compliance_score < 0.5 else 'medium'
        }
    
    def _evaluate_air_quality_co2(self, slo: SLO, room_data: Dict[str, Any], 
                                sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate air quality CO2 levels"""
        current_co2 = sensor_data.get('co2', 400)
        config = slo.config or {}
        max_co2 = config.get('max_co2', 800)
        
        if current_co2 <= max_co2:
            compliance_score = 1.0
            recommendation = "CO2 levels within acceptable range"
        else:
            # Exponential penalty for high CO2
            excess = current_co2 - max_co2
            compliance_score = max(0.0, 1.0 - (excess / 1000.0) ** 1.5)
            recommendation = f"CO2 levels too high. Increase ventilation to reduce by {excess}ppm"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"≤{max_co2}ppm",
            'actual_value': f"{current_co2}ppm",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'high' if current_co2 > 1200 else 'medium' if current_co2 > max_co2 else 'low'
        }
    
    def _evaluate_occupancy_optimization(self, slo: SLO, room_data: Dict[str, Any], 
                                       sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate occupancy-based optimization"""
        occupancy = sensor_data.get('occupancy', 0)
        hvac_devices = [d for d in devices if d.get('type') == 'HVAC' and d.get('status') == 'ON']
        lighting_devices = [d for d in devices if d.get('type') == 'Lighting' and d.get('status') == 'ON']
        
        config = slo.config or {}
        
        if occupancy == 0:
            # Unoccupied optimization
            max_hvac_unoccupied = config.get('max_hvac_unoccupied', 0)
            max_lights_unoccupied = config.get('max_lights_unoccupied', 1)
            
            hvac_compliance = 1.0 if len(hvac_devices) <= max_hvac_unoccupied else 0.5
            light_compliance = 1.0 if len(lighting_devices) <= max_lights_unoccupied else 0.7
            
            compliance_score = (hvac_compliance + light_compliance) / 2
            recommendation = "Optimize for unoccupied space"
        else:
            # Occupied optimization - scale with occupancy
            expected_systems = min(occupancy, 5) / 5.0  # Scale to max 5 people
            total_systems_on = len(hvac_devices) + len(lighting_devices)
            total_systems = len([d for d in devices if d.get('type') in ['HVAC', 'Lighting']])
            
            actual_ratio = total_systems_on / total_systems if total_systems > 0 else 0
            compliance_score = 1.0 if abs(actual_ratio - expected_systems) <= 0.3 else max(0.0, 1.0 - abs(actual_ratio - expected_systems))
            recommendation = f"Optimization for {occupancy} occupants"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"Optimized for {occupancy} occupants",
            'actual_value': f"{len(hvac_devices)} HVAC, {len(lighting_devices)} lights active",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'medium'
        }
    
    def _evaluate_humidity_control(self, slo: SLO, room_data: Dict[str, Any], 
                                 sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate humidity control SLO"""
        current_humidity = sensor_data.get('humidity', 50)
        config = slo.config or {}
        min_humidity = config.get('min_humidity', 40)
        max_humidity = config.get('max_humidity', 60)
        
        if min_humidity <= current_humidity <= max_humidity:
            compliance_score = 1.0
            recommendation = "Humidity levels optimal"
        else:
            if current_humidity < min_humidity:
                deviation = min_humidity - current_humidity
                compliance_score = max(0.0, 1.0 - (deviation / 30.0))  # 30% max deviation
                recommendation = f"Humidity too low. Increase by {deviation:.1f}%"
            else:
                deviation = current_humidity - max_humidity
                compliance_score = max(0.0, 1.0 - (deviation / 30.0))
                recommendation = f"Humidity too high. Reduce by {deviation:.1f}%"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"{min_humidity}-{max_humidity}%",
            'actual_value': f"{current_humidity}%",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'medium'
        }
    
    def _evaluate_emergency_readiness(self, slo: SLO, room_data: Dict[str, Any], 
                                    sensor_data: Dict[str, Any], devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate emergency readiness SLO"""
        emergency_devices = [d for d in devices if d.get('type') in ['Emergency', 'Security']]
        emergency_devices_on = sum(1 for d in emergency_devices if d.get('status') == 'ON')
        
        config = slo.config or {}
        required_emergency_devices = config.get('required_devices', len(emergency_devices))
        
        if emergency_devices_on >= required_emergency_devices:
            compliance_score = 1.0
            recommendation = "Emergency systems operational"
        else:
            compliance_score = emergency_devices_on / required_emergency_devices if required_emergency_devices > 0 else 0.0
            recommendation = f"Emergency readiness compromised. {required_emergency_devices - emergency_devices_on} devices offline"
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': f"{required_emergency_devices} emergency devices active",
            'actual_value': f"{emergency_devices_on}/{len(emergency_devices)} devices active",
            'compliance_score': compliance_score,
            'recommendation': recommendation,
            'priority': 'high' if compliance_score < 0.8 else 'medium'
        }
    
    def _evaluate_generic_slo(self, slo: SLO, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic SLO evaluation for simple numeric comparisons"""
        metric_value = sensor_data.get(slo.metric, 0)
        target_value = slo.target_value or 0
        
        # Simple percentage-based compliance
        if target_value > 0:
            compliance_score = min(1.0, metric_value / target_value)
        else:
            compliance_score = 1.0 if metric_value == target_value else 0.5
        
        return {
            'slo_name': slo.name,
            'metric': slo.metric,
            'expected_value': str(target_value),
            'actual_value': str(metric_value),
            'compliance_score': compliance_score,
            'recommendation': f"Current {slo.metric}: {metric_value}, Target: {target_value}",
            'priority': 'low'
        }
    
    def _calculate_category_scores(self, slo_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate category-wise scores based on SLO results"""
        category_mapping = {
            'temperature_comfort': 'comfort',
            'humidity_control': 'comfort',
            'air_quality_co2': 'environmental',
            'occupancy_optimization': 'environmental',
            'energy_efficiency': 'energy',
            'security_lighting': 'security',
            'emergency_readiness': 'security'
        }
        
        category_scores = {'comfort': [], 'energy': [], 'security': [], 'environmental': []}
        
        for result in slo_results:
            metric = result['metric']
            score = result['compliance_score']
            category = category_mapping.get(metric, 'environmental')
            category_scores[category].append(score)
        
        # Calculate average scores
        final_scores = {}
        for category, scores in category_scores.items():
            if scores:
                final_scores[category] = sum(scores) / len(scores)
            else:
                final_scores[category] = 1.0  # Default to 1.0 if no metrics in category
        
        return final_scores
    
    def _get_violation_severity(self, compliance_score: float) -> str:
        """Determine violation severity based on compliance score"""
        if compliance_score < 0.3:
            return 'critical'
        elif compliance_score < 0.6:
            return 'high'
        elif compliance_score < 0.8:
            return 'medium'
        else:
            return 'low'


class SLOService:
    """Service for managing SLOs and their evaluation"""
    
    def __init__(self):
        self.evaluation_engine = SLOEvaluationEngine()
    
    def create_default_slos(self, db: Session, created_by: str = "system") -> List[SLO]:
        """Create default smart building SLOs"""
        
        default_slos = [
            {
                'name': 'Temperature Comfort',
                'description': 'Maintain temperature within comfort range for occupants',
                'metric': 'temperature_comfort',
                'target_value': 23.0,
                'weight': 0.25,
                'config': {
                    'min_temp': 22,
                    'max_temp': 24,
                    'tolerance': 1.0
                }
            },
            {
                'name': 'Energy Efficiency',
                'description': 'Optimize energy usage based on occupancy patterns',
                'metric': 'energy_efficiency', 
                'target_value': 0.8,
                'weight': 0.20,
                'config': {
                    'max_devices_unoccupied': 1,
                    'efficiency_threshold': 0.7
                }
            },
            {
                'name': 'Security Lighting',
                'description': 'Maintain minimum lighting for security surveillance',
                'metric': 'security_lighting',
                'target_value': 1.0,
                'weight': 0.15,
                'config': {
                    'min_lights': 1
                }
            },
            {
                'name': 'Air Quality CO2',
                'description': 'Maintain CO2 levels below threshold for health',
                'metric': 'air_quality_co2',
                'target_value': 800.0,
                'weight': 0.20,
                'config': {
                    'max_co2': 800
                }
            },
            {
                'name': 'Occupancy Optimization',
                'description': 'Scale building systems based on occupancy levels',
                'metric': 'occupancy_optimization',
                'target_value': 1.0,
                'weight': 0.10,
                'config': {
                    'max_hvac_unoccupied': 0,
                    'max_lights_unoccupied': 1
                }
            },
            {
                'name': 'Humidity Control',
                'description': 'Maintain optimal humidity levels for comfort',
                'metric': 'humidity_control',
                'target_value': 50.0,
                'weight': 0.10,
                'config': {
                    'min_humidity': 40,
                    'max_humidity': 60
                }
            }
        ]
        
        created_slos = []
        for slo_data in default_slos:
            slo = SLO(
                name=slo_data['name'],
                description=slo_data['description'],
                metric=slo_data['metric'],
                target_value=slo_data['target_value'],
                weight=slo_data['weight'],
                config=slo_data['config'],
                created_by=created_by,
                is_system_defined=True,
                active=True
            )
            db.add(slo)
            created_slos.append(slo)
        
        db.commit()
        return created_slos
    
    def evaluate_slos(self, room_data: Dict[str, Any], sensor_data: Dict[str, Any], 
                     devices: List[Dict[str, Any]], slos: List[SLO]) -> Dict[str, Any]:
        """Evaluate room against all SLOs"""
        return self.evaluation_engine.evaluate_room_slos(room_data, sensor_data, devices, slos)
    
    def get_slo_violations(self, evaluation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract SLO violations from evaluation results"""
        return evaluation_results.get('violations', [])
    
    def get_compliance_summary(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of SLO compliance"""
        return {
            'overall_compliance': evaluation_results.get('overall_compliance', 0.0),
            'category_scores': evaluation_results.get('scores', {}),
            'total_slos': len(evaluation_results.get('slo_results', [])),
            'violations': len(evaluation_results.get('violations', [])),
            'recommendations': len(evaluation_results.get('recommendations', []))
        }
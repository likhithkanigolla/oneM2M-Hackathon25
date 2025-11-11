"""
IoT Sensor Data Service

This service handles sensor data ingestion, processing, and provides
aggregated sensor data to LLM agents for decision making.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.database import get_db
from app.models.sensor import Sensor, SensorData, SensorAlert, SensorType

class SensorDataService:
    """Service for managing IoT sensor data"""
    
    def __init__(self, db: Session):
        self.db = db

    def ingest_sensor_data(self, sensor_id: str, value: float, 
                          quality: str = "good", metadata: Dict = None) -> SensorData:
        """
        Ingest new sensor data reading
        
        Args:
            sensor_id: Unique sensor identifier
            value: Sensor reading value
            quality: Data quality indicator
            metadata: Additional reading context
            
        Returns:
            Created SensorData instance
        """
        # Verify sensor exists and is active
        sensor = self.db.query(Sensor).filter(Sensor.id == sensor_id, Sensor.active == True).first()
        if not sensor:
            raise ValueError(f"Sensor {sensor_id} not found or inactive")
        
        # Create sensor data entry
        sensor_data = SensorData(
            sensor_id=sensor_id,
            value=value,
            quality=quality,
            metadata=metadata or {}
        )
        
        self.db.add(sensor_data)
        self.db.commit()
        self.db.refresh(sensor_data)
        
        # Check for alert conditions
        self._check_alert_conditions(sensor, value)
        
        return sensor_data

    def get_latest_sensor_data(self, room_id: int) -> Dict[str, Any]:
        """
        Get latest sensor readings for a specific room
        
        Args:
            room_id: Room identifier
            
        Returns:
            Dictionary with latest sensor values by type
        """
        # Get all sensors for the room
        sensors = self.db.query(Sensor).filter(
            Sensor.room_id == room_id, 
            Sensor.active == True
        ).all()
        
        sensor_data = {}
        
        for sensor in sensors:
            # Get latest reading for each sensor
            latest_reading = self.db.query(SensorData).filter(
                SensorData.sensor_id == sensor.id
            ).order_by(desc(SensorData.timestamp)).first()
            
            if latest_reading:
                sensor_data[sensor.sensor_type] = {
                    "value": latest_reading.value,
                    "unit": sensor.unit,
                    "timestamp": latest_reading.timestamp.isoformat(),
                    "quality": latest_reading.quality,
                    "sensor_id": sensor.id,
                    "location": sensor.location
                }
        
        return sensor_data

    def get_sensor_history(self, sensor_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get historical sensor data for specified time period
        
        Args:
            sensor_id: Sensor identifier
            hours: Number of hours of history to retrieve
            
        Returns:
            List of sensor readings with timestamps
        """
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        readings = self.db.query(SensorData).filter(
            and_(
                SensorData.sensor_id == sensor_id,
                SensorData.timestamp >= start_time
            )
        ).order_by(SensorData.timestamp).all()
        
        return [reading.to_dict() for reading in readings]

    def get_room_environmental_summary(self, room_id: int) -> Dict[str, Any]:
        """
        Get comprehensive environmental summary for LLM agents
        
        Args:
            room_id: Room identifier
            
        Returns:
            Environmental data formatted for LLM consumption
        """
        latest_data = self.get_latest_sensor_data(room_id)
        
        # Get alerts for the room
        active_alerts = self.get_active_alerts(room_id)
        
        # Calculate derived metrics
        comfort_score = self._calculate_comfort_score(latest_data)
        air_quality_index = self._calculate_air_quality_index(latest_data)
        
        return {
            "room_id": room_id,
            "timestamp": datetime.utcnow().isoformat(),
            "sensors": latest_data,
            "derived_metrics": {
                "comfort_score": comfort_score,
                "air_quality_index": air_quality_index,
                "occupancy_detected": latest_data.get("occupancy", {}).get("value", 0) > 0,
                "motion_detected": latest_data.get("motion", {}).get("value", 0) > 0
            },
            "active_alerts": active_alerts,
            "data_quality": self._assess_data_quality(latest_data)
        }

    def get_active_alerts(self, room_id: int) -> List[Dict[str, Any]]:
        """Get active sensor alerts for a room"""
        sensors = self.db.query(Sensor).filter(Sensor.room_id == room_id).all()
        sensor_ids = [s.id for s in sensors]
        
        alerts = self.db.query(SensorAlert).filter(
            and_(
                SensorAlert.sensor_id.in_(sensor_ids),
                SensorAlert.resolved_at.is_(None)
            )
        ).all()
        
        return [alert.to_dict() for alert in alerts]

    def create_mock_sensor_data(self, room_id: int) -> Dict[str, Any]:
        """
        Create mock sensor data for testing LLM agents
        This simulates realistic IoT sensor readings
        """
        import random
        
        current_time = datetime.utcnow()
        base_temp = 22.0 + random.uniform(-2, 2)  # 20-24°C
        base_humidity = 45 + random.uniform(-10, 15)  # 35-60%
        
        mock_data = {
            "temperature": {
                "value": round(base_temp, 1),
                "unit": "°C",
                "timestamp": current_time.isoformat(),
                "quality": "good",
                "sensor_id": f"temp_sensor_{room_id}",
                "location": "center"
            },
            "humidity": {
                "value": round(base_humidity, 1),
                "unit": "%RH",
                "timestamp": current_time.isoformat(),
                "quality": "good", 
                "sensor_id": f"humidity_sensor_{room_id}",
                "location": "center"
            },
            "co2": {
                "value": round(400 + random.uniform(0, 600)),  # 400-1000 ppm
                "unit": "ppm",
                "timestamp": current_time.isoformat(),
                "quality": "good",
                "sensor_id": f"co2_sensor_{room_id}",
                "location": "center"
            },
            "occupancy": {
                "value": random.randint(0, 8),  # 0-8 people
                "unit": "people",
                "timestamp": current_time.isoformat(),
                "quality": "good",
                "sensor_id": f"occupancy_sensor_{room_id}",
                "location": "entrance"
            },
            "light_level": {
                "value": round(200 + random.uniform(0, 400)),  # 200-600 lux
                "unit": "lux",
                "timestamp": current_time.isoformat(),
                "quality": "good",
                "sensor_id": f"light_sensor_{room_id}",
                "location": "center"
            },
            "motion": {
                "value": 1 if random.random() > 0.7 else 0,  # 30% chance of motion
                "unit": "boolean",
                "timestamp": current_time.isoformat(),
                "quality": "good",
                "sensor_id": f"motion_sensor_{room_id}",
                "location": "ceiling"
            },
            "noise": {
                "value": round(35 + random.uniform(0, 25)),  # 35-60 dB
                "unit": "dB",
                "timestamp": current_time.isoformat(),
                "quality": "good",
                "sensor_id": f"noise_sensor_{room_id}",
                "location": "center"
            }
        }
        
        return {
            "room_id": room_id,
            "timestamp": current_time.isoformat(),
            "sensors": mock_data,
            "derived_metrics": {
                "comfort_score": self._calculate_comfort_score(mock_data),
                "air_quality_index": self._calculate_air_quality_index(mock_data),
                "occupancy_detected": mock_data["occupancy"]["value"] > 0,
                "motion_detected": mock_data["motion"]["value"] > 0
            },
            "active_alerts": [],
            "data_quality": "good"
        }

    def _check_alert_conditions(self, sensor: Sensor, value: float):
        """Check if sensor reading triggers any alerts"""
        # Define alert thresholds by sensor type
        thresholds = {
            SensorType.TEMPERATURE: {"min": 15, "max": 30},
            SensorType.HUMIDITY: {"min": 20, "max": 80},
            SensorType.CO2: {"max": 1500},
            SensorType.LIGHT_LEVEL: {"min": 50},
            SensorType.NOISE_LEVEL: {"max": 80},
        }
        
        if sensor.sensor_type in thresholds:
            limits = thresholds[sensor.sensor_type]
            
            if "min" in limits and value < limits["min"]:
                self._create_alert(sensor.id, "threshold_low", "warning", 
                                 f"{sensor.sensor_type} below minimum threshold", 
                                 limits["min"], value)
            elif "max" in limits and value > limits["max"]:
                self._create_alert(sensor.id, "threshold_high", "warning",
                                 f"{sensor.sensor_type} above maximum threshold",
                                 limits["max"], value)

    def _create_alert(self, sensor_id: str, alert_type: str, severity: str,
                     message: str, threshold_value: float = None, actual_value: float = None):
        """Create a new sensor alert"""
        alert = SensorAlert(
            sensor_id=sensor_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            threshold_value=threshold_value,
            actual_value=actual_value
        )
        self.db.add(alert)
        self.db.commit()

    def _calculate_comfort_score(self, sensor_data: Dict) -> float:
        """Calculate overall comfort score from sensor data"""
        score = 100.0
        
        # Temperature comfort (optimal 22°C)
        if "temperature" in sensor_data:
            temp = sensor_data["temperature"]["value"]
            temp_deviation = abs(temp - 22)
            score -= min(temp_deviation * 5, 30)  # Max 30 point penalty
        
        # Humidity comfort (optimal 50%)
        if "humidity" in sensor_data:
            humidity = sensor_data["humidity"]["value"]
            if humidity < 30 or humidity > 70:
                score -= 20
            elif humidity < 40 or humidity > 60:
                score -= 10
        
        # CO2 comfort
        if "co2" in sensor_data:
            co2 = sensor_data["co2"]["value"]
            if co2 > 1000:
                score -= 25
            elif co2 > 800:
                score -= 10
        
        return max(0, min(100, score))

    def _calculate_air_quality_index(self, sensor_data: Dict) -> int:
        """Calculate air quality index from sensor data"""
        # Simplified AQI calculation based on CO2 and other factors
        aqi = 100
        
        if "co2" in sensor_data:
            co2 = sensor_data["co2"]["value"]
            if co2 > 1500:
                aqi = 200  # Unhealthy
            elif co2 > 1000:
                aqi = 150  # Unhealthy for sensitive groups
            elif co2 > 800:
                aqi = 100  # Moderate
            else:
                aqi = 50   # Good
        
        return aqi

    def _assess_data_quality(self, sensor_data: Dict) -> str:
        """Assess overall data quality"""
        if not sensor_data:
            return "no_data"
        
        quality_indicators = [data.get("quality", "unknown") for data in sensor_data.values()]
        
        if all(q == "good" for q in quality_indicators):
            return "good"
        elif any(q == "error" for q in quality_indicators):
            return "error"
        elif any(q == "poor" for q in quality_indicators):
            return "poor"
        else:
            return "fair"
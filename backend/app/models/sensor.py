"""
IoT Sensor Data Models and Integration

This module defines models for IoT sensor data that feeds into
the LLM agent decision-making system.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class SensorType:
    """Enumeration of supported sensor types"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    OCCUPANCY = "occupancy"
    MOTION = "motion"
    CO2 = "co2"
    AIR_QUALITY = "air_quality"
    LIGHT_LEVEL = "light_level"
    NOISE_LEVEL = "noise"
    DOOR_SENSOR = "door"
    WINDOW_SENSOR = "window"
    SMOKE_DETECTOR = "smoke"
    FIRE_ALARM = "fire_alarm"
    SECURITY_CAMERA = "camera"
    ACCESS_CONTROL = "access"
    ENERGY_METER = "energy"
    WATER_SENSOR = "water"
    PRESSURE = "pressure"
    VOC = "voc"  # Volatile Organic Compounds
    PM25 = "pm25"  # Particulate Matter 2.5

class Sensor(Base):
    """IoT Sensor device information"""
    __tablename__ = "sensors"

    id = Column(String, primary_key=True)  # Sensor device ID
    name = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)  # From SensorType
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    location = Column(String, nullable=True)  # Specific location within room
    unit = Column(String, nullable=True)  # e.g., "°C", "ppm", "lux"
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)  # Sensor accuracy/precision
    calibration_date = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    sensor_metadata = Column(JSON, nullable=True)  # Additional sensor configuration

    # Relationships
    room = relationship("Room", back_populates="sensors")
    sensor_data = relationship("SensorData", back_populates="sensor", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sensor_type": self.sensor_type,
            "room_id": self.room_id,
            "location": self.location,
            "unit": self.unit,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "accuracy": self.accuracy,
            "calibration_date": self.calibration_date.isoformat() if self.calibration_date else None,
            "active": self.active,
            "sensor_metadata": self.sensor_metadata,
        }

class SensorData(Base):
    """Time-series sensor data readings"""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    value = Column(Float, nullable=False)
    quality = Column(String, default="good")  # good, poor, error, calibrating
    battery_level = Column(Float, nullable=True)  # For battery-powered sensors
    signal_strength = Column(Float, nullable=True)  # Wireless signal strength
    reading_metadata = Column(JSON, nullable=True)  # Additional reading context

    # Relationships
    sensor = relationship("Sensor", back_populates="sensor_data")

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "quality": self.quality,
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
            "reading_metadata": self.reading_metadata,
        }

class SensorAlert(Base):
    """Sensor-based alerts and threshold violations"""
    __tablename__ = "sensor_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # threshold_high, threshold_low, malfunction, battery_low
    severity = Column(String, nullable=False)  # critical, warning, info
    message = Column(String, nullable=False)
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolution_notes = Column(String, nullable=True)

    # Relationships
    sensor = relationship("Sensor")

    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolution_notes": self.resolution_notes,
        }
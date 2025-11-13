from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.sensor import Sensor, SensorData

router = APIRouter()

@router.post("/snapshot")
async def post_sensor_snapshot(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Accept a sensor snapshot (single reading) and persist to sensor_data.
    Payload: { sensor_id, value, quality?, battery_level?, signal_strength?, reading_metadata? }
    """
    sensor_id = payload.get('sensor_id')
    value = payload.get('value')
    if sensor_id is None or value is None:
        raise HTTPException(status_code=400, detail="sensor_id and value are required")

    sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    sd = SensorData(
        sensor_id=sensor_id,
        timestamp=datetime.utcnow(),
        value=float(value),
        quality=payload.get('quality', 'good'),
        battery_level=payload.get('battery_level'),
        signal_strength=payload.get('signal_strength'),
        reading_metadata=payload.get('reading_metadata')
    )

    db.add(sd)
    db.commit()
    db.refresh(sd)

    return {"status": "ok", "sensor_data_id": sd.id}

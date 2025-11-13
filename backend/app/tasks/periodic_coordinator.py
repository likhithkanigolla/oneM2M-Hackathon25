import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from app.database import SessionLocal
from app.models.room import Room
from app.models.device import Device
from app.models.sensor import Sensor, SensorData
from app.models.slo import SLO
from app.models.decision_log import DecisionLog
from app.models.agent import Agent
from app.services.decision_coordinator import MultiAgentCoordinator

# Config via environment variables is handled in app.config; use defaults here
COORDINATOR_INTERVAL_SECONDS = int(__import__('os').environ.get('COORDINATOR_INTERVAL_SECONDS', '300'))
COORDINATOR_ENABLED = __import__('os').environ.get('COORDINATOR_ENABLED', 'true').lower() in ('1','true','yes')

coordinator = MultiAgentCoordinator()


def _build_sensor_snapshot(db, room_id: int) -> Dict[str, Any]:
    # Get latest sensor_data values for sensors in the room
    sensors = db.query(Sensor).filter(Sensor.room_id == room_id).all()
    snapshot = {}
    for s in sensors:
        # get latest reading for this sensor
        sd = db.query(SensorData).filter(SensorData.sensor_id == s.id).order_by(SensorData.timestamp.desc()).first()
        if sd:
            snapshot[s.sensor_type] = sd.value
    return snapshot


async def run_once_for_all_rooms():
    db = SessionLocal()
    try:
        rooms = db.query(Room).all()
        slos = db.query(SLO).filter(SLO.active == True).all()
        for room in rooms:
            try:
                # devices
                devices = db.query(Device).filter(Device.room_id == room.id).all()
                device_data = [d.to_dict() for d in devices]

                # sensor snapshot
                sensor_data = _build_sensor_snapshot(db, room.id)
                # fallback mock values if empty
                sensor_data.setdefault('temperature', 22.5)
                sensor_data.setdefault('humidity', 45)
                sensor_data.setdefault('co2', 400)
                sensor_data.setdefault('occupancy', 0)
                sensor_data.setdefault('light_level', 300)

                context = {
                    'room_data': room.to_dict(),
                    'devices': device_data,
                    'sensor_data': sensor_data,
                    'slos': [s.to_dict() for s in slos],
                    'timestamp': datetime.now().isoformat()
                }

                # coordinate
                decision_plans = await coordinator.coordinate_decisions(context, slos)

                # persist agent decisions (one DecisionLog per agent decision)
                for agent_decision in context.get('agent_decisions', []) or []:
                    pass

                # The coordinator returns DecisionPlan objects. We also have raw agent decisions
                # in the decision plans' agent_decisions field. Persist those per-agent.
                for plan in decision_plans:
                    for ad in plan.agent_decisions:
                        agent_id = ad.get('agent_id') or ad.get('agent') or 'unknown'

                        # Ensure Agent record exists to satisfy FK constraint
                        existing_agent = db.query(Agent).filter(Agent.id == agent_id).first()
                        if not existing_agent:
                            try:
                                new_agent = Agent(id=agent_id, name=agent_id, goal=ad.get('agent_type') or None, active=True, weight=0.5)
                                db.add(new_agent)
                                db.flush()  # ensure id is available for FK
                            except Exception:
                                db.rollback()
                                # If agent creation fails, skip logging this particular agent decision
                                print(f"Warning: failed to create Agent row for {agent_id}; skipping DecisionLog insertion")
                                continue

                        dl = DecisionLog(
                            timestamp=datetime.utcnow(),
                            agent_id=agent_id,
                            room_id=room.id,
                            decision=json.dumps(ad.get('decisions', [])),
                            reasoning=ad.get('reasoning', ''),
                            comfort_score=ad.get('scores', {}).get('comfort'),
                            energy_score=ad.get('scores', {}).get('energy'),
                            reliability_score=ad.get('scores', {}).get('reliability'),
                            context={'sensor_snapshot': sensor_data, 'plan_id': plan.plan_id}
                        )
                        db.add(dl)

                # update room summary (top plan)
                top_plan = decision_plans[0] if decision_plans else None
                if top_plan:
                    room.last_coordinated_at = datetime.utcnow()
                    room.last_coordination_summary = {
                        'plan_id': top_plan.plan_id,
                        'score': top_plan.score,
                        'confidence': top_plan.confidence,
                        'actions': top_plan.actions,
                        'metadata': top_plan.metadata,
                        'slo_compliance': top_plan.slo_compliance
                    }

                db.commit()

            except Exception as e:
                db.rollback()
                print(f"Error coordinating for room {room.id}: {e}")
    finally:
        db.close()


async def periodic_coordinator_loop():
    if not COORDINATOR_ENABLED:
        print("Coordinator disabled by environment variable COORDINATOR_ENABLED")
        return

    print(f"Starting periodic coordinator loop (interval={COORDINATOR_INTERVAL_SECONDS}s)")
    while True:
        try:
            await run_once_for_all_rooms()
        except Exception as e:
            print(f"Periodic coordinator run failed: {e}")
        await asyncio.sleep(COORDINATOR_INTERVAL_SECONDS)


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.create_task(periodic_coordinator_loop())

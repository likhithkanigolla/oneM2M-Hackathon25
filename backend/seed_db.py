"""Seed the database using SQLAlchemy models.

Run with:
  python seed_db.py

This script connects to the DATABASE_URL from config and inserts sample data.
"""
from app.config import settings
from app.database import engine, SessionLocal, Base
from app.models.room import Room
from app.models.device import Device, DeviceStatus
from app.models.agent import Agent
from app.models.slo import SLO
from app.models.scenario import Scenario
from app.models.user import User

def create_sample(session):
    # create rooms and devices similar to frontend defaults
    r1 = Room(name="Conference Room A", gsi=0.84, aq=85, temp=24, occupancy=5, position={"x":100,"y":100})
    r2 = Room(name="Conference Room B", gsi=0.76, aq=78, temp=26, occupancy=3, position={"x":350,"y":100})
    r3 = Room(name="Office Space", gsi=0.92, aq=92, temp=23, occupancy=8, position={"x":100,"y":300})
    r4 = Room(name="Lab Room", gsi=0.68, aq=72, temp=27, occupancy=2, position={"x":350,"y":300})

    session.add_all([r1, r2, r3, r4])
    session.commit()

    # devices for r1
    d1 = Device(name="AC", type="HVAC", status=DeviceStatus.ON, room_id=r1.id, services=[{"name":"TempFromWeatherStation","inputSource":"Weather Node","active":True,"controlledBy":"Claude"}])
    d2 = Device(name="Light", type="Lighting", status=DeviceStatus.ON, room_id=r1.id, services=[{"name":"CameraLighting","inputSource":"Camera Sensor","active":True,"controlledBy":"Gemini"}])
    d3 = Device(name="Fan", type="AirFlow", status=DeviceStatus.ON, room_id=r1.id, services=[{"name":"CirculateAir","inputSource":"Occupancy Sensor","active":True,"controlledBy":"Gemini"}])
    d4 = Device(name="Camera", type="Security", status=DeviceStatus.ON, room_id=r1.id, services=[{"name":"Monitoring","inputSource":"Motion Sensor","active":True,"controlledBy":"GPT"}])

    session.add_all([d1, d2, d3, d4])
    session.commit()

    # Create AI agents
    agent1 = Agent(id="gemini", name="Gemini AI", goal="Optimize comfort and air quality", rag_sources=["sensor", "comfort"], active=True, weight=0.4)
    agent2 = Agent(id="claude", name="Claude AI", goal="Energy efficiency optimization", rag_sources=["energy", "weather"], active=True, weight=0.35)
    agent3 = Agent(id="gpt", name="GPT AI", goal="Security and reliability", rag_sources=["security", "reliability"], active=True, weight=0.25)
    
    session.add_all([agent1, agent2, agent3])
    session.commit()

    # Create SLOs
    slo1 = SLO(name="Comfort", description="Maintain comfortable environment", target_value=0.85, metric="comfort_score")
    slo2 = SLO(name="Energy Efficiency", description="Optimize energy consumption", target_value=0.80, metric="energy_score")
    slo3 = SLO(name="Reliability", description="System reliability and uptime", target_value=0.95, metric="reliability_score")
    
    session.add_all([slo1, slo2, slo3])
    session.commit()

    # Create scenarios
    scenario1 = Scenario(name="Meeting Priority", description="Prioritize comfort during meetings", active=False, config={"priority": "comfort", "energy_reduction": 0.1})
    scenario2 = Scenario(name="Energy Shortage", description="Reduce energy consumption", active=False, config={"max_energy": 0.7, "comfort_reduction": 0.2})
    scenario3 = Scenario(name="System Active", description="Normal operation mode", active=True, config={"balanced": True})
    
    session.add_all([scenario1, scenario2, scenario3])
    session.commit()

    # Create users
    user1 = User(username="admin", email="admin@smartroom.com", is_admin=True, hashed_password="admin123")
    user2 = User(username="operator", email="operator@smartroom.com", is_admin=False, hashed_password="operator123")
    
    session.add_all([user1, user2])
    session.commit()

    print("Seed data created")

if __name__ == "__main__":
    # Create tables if not exists
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_sample(db)
    finally:
        db.close()

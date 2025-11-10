from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioBase, ScenarioCreate, ScenarioUpdate

router = APIRouter()

@router.get("/", response_model=List[ScenarioBase])
async def get_scenarios(db: Session = Depends(get_db)):
    """Get all scenarios"""
    return db.query(Scenario).all()

@router.get("/active", response_model=List[ScenarioBase])
async def get_active_scenarios(db: Session = Depends(get_db)):
    """Get only active scenarios"""
    return db.query(Scenario).filter(Scenario.active == True).all()

@router.get("/{scenario_id}", response_model=ScenarioBase)
async def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Get specific scenario by ID"""
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.post("/", response_model=ScenarioBase)
async def create_scenario(scenario: ScenarioCreate, db: Session = Depends(get_db)):
    """Create new scenario"""
    db_scenario = Scenario(**scenario.dict())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

@router.put("/{scenario_id}", response_model=ScenarioBase)
async def update_scenario(scenario_id: int, scenario: ScenarioUpdate, db: Session = Depends(get_db)):
    """Update scenario"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    for field, value in scenario.dict(exclude_unset=True).items():
        setattr(db_scenario, field, value)
    
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Delete scenario"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    db.delete(db_scenario)
    db.commit()
    return {"message": "Scenario deleted successfully"}

@router.patch("/{scenario_id}/toggle")
async def toggle_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Toggle scenario active status"""
    db_scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not db_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    db_scenario.active = not db_scenario.active
    db.commit()
    db.refresh(db_scenario)
    return db_scenario
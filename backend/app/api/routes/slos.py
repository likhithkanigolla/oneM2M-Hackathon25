from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.slo import SLO
from app.schemas.slo import SLOBase, SLOCreate, SLOUpdate

router = APIRouter()

@router.get("/", response_model=List[SLOBase])
async def get_slos(db: Session = Depends(get_db)):
    """Get all SLOs"""
    return db.query(SLO).all()

@router.get("/{slo_id}", response_model=SLOBase)
async def get_slo(slo_id: int, db: Session = Depends(get_db)):
    """Get specific SLO by ID"""
    slo = db.query(SLO).filter(SLO.id == slo_id).first()
    if not slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    return slo

@router.post("/", response_model=SLOBase)
async def create_slo(slo: SLOCreate, db: Session = Depends(get_db)):
    """Create new SLO"""
    db_slo = SLO(**slo.dict())
    db.add(db_slo)
    db.commit()
    db.refresh(db_slo)
    return db_slo

@router.put("/{slo_id}", response_model=SLOBase)
async def update_slo(slo_id: int, slo: SLOUpdate, db: Session = Depends(get_db)):
    """Update SLO"""
    db_slo = db.query(SLO).filter(SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    
    for field, value in slo.dict(exclude_unset=True).items():
        setattr(db_slo, field, value)
    
    db.commit()
    db.refresh(db_slo)
    return db_slo

@router.delete("/{slo_id}")
async def delete_slo(slo_id: int, db: Session = Depends(get_db)):
    """Delete SLO"""
    db_slo = db.query(SLO).filter(SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    
    db.delete(db_slo)
    db.commit()
    return {"message": "SLO deleted successfully"}
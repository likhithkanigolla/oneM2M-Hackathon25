from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.slo import SLO
from app.schemas.slo import SLOBase, SLOCreate, SLOUpdate, SLOResponse
from app.auth import get_current_user, require_admin
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[SLOResponse])
async def get_slos(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all SLOs - authenticated users can view all SLOs"""
    return db.query(SLO).all()

@router.get("/{slo_id}", response_model=SLOResponse)
async def get_slo(slo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get specific SLO by ID"""
    slo = db.query(SLO).filter(SLO.id == slo_id).first()
    if not slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    return slo

@router.post("/", response_model=SLOResponse)
async def create_slo(slo: SLOCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new SLO - both operators and admins can create SLOs"""
    # Determine if this is a system-defined SLO (only admins can create these)
    is_system_defined = slo.is_system_defined and current_user.role == "admin"
    
    db_slo = SLO(
        name=slo.name,
        description=slo.description,
        target_value=slo.target_value,
        metric=slo.metric,
        weight=slo.weight,
        active=slo.active,
        config=slo.config,
        created_by=current_user.username,
        is_system_defined=is_system_defined
    )
    db.add(db_slo)
    db.commit()
    db.refresh(db_slo)
    return db_slo

@router.put("/{slo_id}", response_model=SLOResponse)
async def update_slo(slo_id: int, slo: SLOUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update SLO - only owner or admin can update"""
    db_slo = db.query(SLO).filter(SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    
    # Check permissions: admin can edit all, operators can only edit their own
    if current_user.role != "admin" and db_slo.created_by != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to update this SLO")
    
    for field, value in slo.dict(exclude_unset=True).items():
        setattr(db_slo, field, value)
    
    db.commit()
    db.refresh(db_slo)
    return db_slo

@router.delete("/{slo_id}")
async def delete_slo(slo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete SLO with role-based permissions"""
    db_slo = db.query(SLO).filter(SLO.id == slo_id).first()
    if not db_slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    
    # Permission rules:
    # - Admins can delete any SLO
    # - Operators can delete their own SLOs UNLESS it's system-defined
    if current_user.role == "admin":
        # Admin can delete any SLO
        pass
    elif current_user.role == "operator":
        if db_slo.is_system_defined:
            raise HTTPException(status_code=403, detail="Cannot delete system-defined SLO")
        if db_slo.created_by != current_user.username:
            raise HTTPException(status_code=403, detail="Can only delete your own SLOs")
    else:
        raise HTTPException(status_code=403, detail="Not authorized to delete SLOs")
    
    db.delete(db_slo)
    db.commit()
    return {"message": "SLO deleted successfully"}
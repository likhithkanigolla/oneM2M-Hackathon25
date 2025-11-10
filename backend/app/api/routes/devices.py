from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.device import Device, DeviceStatus
from app.models.room import Room
from app.schemas.device import DeviceBase, DeviceCreate, DeviceUpdate, DeviceResponse
from app.auth import require_admin, get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=DeviceResponse)
async def create_device(device: DeviceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Create new device (admin only)"""
    # Verify room exists
    room = db.query(Room).filter(Room.id == device.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    db_device = Device(
        name=device.name,
        type=device.type,
        status=DeviceStatus(device.status) if device.status else DeviceStatus.OFF,
        room_id=device.room_id,
        services=device.services or []
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@router.get("/room/{room_id}", response_model=List[DeviceResponse])
async def get_room_devices(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all devices in a room"""
    # Check if room exists
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user has access to this room
    if current_user.role != "admin":
        if not current_user.assigned_rooms or room_id not in current_user.assigned_rooms:
            raise HTTPException(status_code=403, detail="Access denied to this room")
    
    return db.query(Device).filter(Device.room_id == room_id).all()

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get specific device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check if user has access to this device's room
    if current_user.role != "admin":
        if not current_user.assigned_rooms or device.room_id not in current_user.assigned_rooms:
            raise HTTPException(status_code=403, detail="Access denied to this device")
    
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Update device (admin only)"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Update only provided fields
    update_data = device.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            setattr(db_device, field, DeviceStatus(value))
        else:
            setattr(db_device, field, value)
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

@router.delete("/{device_id}")
async def delete_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Delete device (admin only)"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(db_device)
    db.commit()
    return {"message": "Device deleted successfully"}

@router.patch("/{device_id}/status")
async def update_device_status(device_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update device status (authenticated users for their assigned rooms)"""
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check if user has access to this device's room
    if current_user.role != "admin":
        if not current_user.assigned_rooms or db_device.room_id not in current_user.assigned_rooms:
            raise HTTPException(status_code=403, detail="Access denied to control this device")
    
    try:
        db_device.status = DeviceStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value. Must be 'ON' or 'OFF'")
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.room_service import RoomService
from app.schemas.room import RoomBase, RoomCreate, RoomUpdate
from app.auth import require_admin
from app.models.user import User
from app.utils.websocket import manager

router = APIRouter()

@router.get("/", response_model=List[RoomBase])
async def get_rooms(db: Session = Depends(get_db)):
    service = RoomService(db)
    return service.get_all_rooms()

@router.get("/{room_id}", response_model=RoomBase)
async def get_room(room_id: int, db: Session = Depends(get_db)):
    service = RoomService(db)
    room = service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/", response_model=RoomBase)
async def create_room(room: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Create new room (admin only)"""
    service = RoomService(db)
    return service.create_room(room)

@router.put("/{room_id}", response_model=RoomBase)
async def update_room(room_id: int, room: RoomUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Update room (admin only)"""
    service = RoomService(db)
    updated_room = service.update_room(room_id, room)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated_room

@router.delete("/{room_id}")
async def delete_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Delete room (admin only)"""
    service = RoomService(db)
    if not service.delete_room(room_id):
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"}


@router.patch("/{room_id}/devices/{device_name}")
async def update_device(
    room_id: int,
    device_name: str,
    status: str,
    db: Session = Depends(get_db),
):
    """Update device status (manual override)"""
    service = RoomService(db)
    updated_room = service.update_device_status(room_id, device_name, status)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Room or device not found")

    # Broadcast update via WebSocket (send dict)
    await manager.broadcast_room_update(updated_room.to_dict())

    return updated_room

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await manager.connect(websocket)
    try:
        while True:
            # keep connection alive
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

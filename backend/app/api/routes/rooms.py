from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.room_service import RoomService
from app.schemas.room import RoomBase
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

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await manager.connect(websocket)
    try:
        while True:
            # keep connection alive
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

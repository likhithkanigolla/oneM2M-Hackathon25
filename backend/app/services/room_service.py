from sqlalchemy.orm import Session
from app.models.room import Room
from app.models.device import Device
from app.models.device import DeviceStatus
from app.schemas.room import RoomCreate, RoomUpdate

class RoomService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_rooms(self):
        return self.db.query(Room).all()

    def get_room(self, room_id: int):
        return self.db.query(Room).filter(Room.id == room_id).first()

    def create_room(self, room_data: RoomCreate):
        room = Room(
            name=room_data.name,
            gsi=room_data.gsi or 0.0,
            aq=room_data.aq,
            temp=room_data.temp,
            occupancy=room_data.occupancy or 0,
            position=room_data.position
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def update_room(self, room_id: int, room_data: RoomUpdate):
        room = self.get_room(room_id)
        if not room:
            return None
        
        # Update only provided fields
        update_data = room_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)
        
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete_room(self, room_id: int):
        room = self.get_room(room_id)
        if not room:
            return False
        
        self.db.delete(room)
        self.db.commit()
        return True

    def update_device_status(self, room_id: int, device_name: str, status: str):
        room = self.get_room(room_id)
        if not room:
            return None
        device = next((d for d in room.devices if d.name == device_name), None)
        if not device:
            return None
        # Accept either string or enum
        try:
            device.status = DeviceStatus(status)
        except Exception:
            # fallback: assign raw string (SQLAlchemy may coerce)
            device.status = status
        self.db.add(device)
        self.db.commit()
        self.db.refresh(room)
        return room

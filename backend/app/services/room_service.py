from sqlalchemy.orm import Session
from app.models.room import Room
from app.models.device import Device

class RoomService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_rooms(self):
        return self.db.query(Room).all()

    def get_room(self, room_id: int):
        return self.db.query(Room).filter(Room.id == room_id).first()

    def update_device_status(self, room_id: int, device_name: str, status: str):
        room = self.get_room(room_id)
        if not room:
            return None
        device = next((d for d in room.devices if d.name == device_name), None)
        if not device:
            return None
        device.status = status
        self.db.add(device)
        self.db.commit()
        self.db.refresh(room)
        return room

from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast_room_update(self, room_data: Dict):
        message = json.dumps({
            "type": "room_update",
            "data": room_data,
        })
        for connection in list(self.active_connections):
            await connection.send_text(message)

    async def broadcast_decision(self, decision_data: Dict):
        message = json.dumps({
            "type": "agent_decision",
            "data": decision_data,
        })
        for connection in list(self.active_connections):
            await connection.send_text(message)

manager = ConnectionManager()

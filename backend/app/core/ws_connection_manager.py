from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, patient_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[patient_id] = websocket

    def disconnect(self, patient_id: int):
        if patient_id in self.active_connections:
            del self.active_connections[patient_id]

    async def send_personal_message(self, message: dict, patient_id: int):
        if patient_id in self.active_connections:
            await self.active_connections[patient_id].send_json(message)


manager = ConnectionManager()

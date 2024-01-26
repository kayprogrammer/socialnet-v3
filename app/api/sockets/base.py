import json
from fastapi import WebSocket


class BaseSocketConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        await websocket.close()

    async def receive_data(self, websocket: WebSocket):
        data = None
        err = None
        try:
            data = await websocket.receive_json()
        except json.decoder.JSONDecodeError:
            err = "Invalid JSON"
        return data, err

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)

    async def send_error_data(
        self, websocket: WebSocket, message, code=4000, data=None
    ):
        err_data = {"status": "error", "code": code, "message": message}
        if data:
            err_data["data"] = data
        await websocket.send_json(err_data)
        await self.disconnect(websocket)

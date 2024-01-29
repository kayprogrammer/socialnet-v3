import json
from fastapi import WebSocket, WebSocketException

from app.common.handlers import ErrorCode


class BaseSocketConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    def disconnect(self, code, reason):
        raise WebSocketException(code, reason)

    async def receive_data(self, websocket: WebSocket):
        try:
            data = await websocket.receive_json()
        except json.decoder.JSONDecodeError:
            await self.send_error_data(
                websocket, "Invalid JSON", ErrorCode.INVALID_DATA_TYPE
            )
        return data

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection.send_json(data)

    async def send_error_data(
        self,
        websocket: WebSocket,
        message,
        err_type=ErrorCode.BAD_REQUEST,
        code=4000,
        data=None,
    ):
        err_data = {
            "status": "error",
            "type": err_type,
            "code": code,
            "message": message,
        }
        if data:
            err_data["data"] = data
        await websocket.send_json(err_data)
        self.disconnect(code, message)

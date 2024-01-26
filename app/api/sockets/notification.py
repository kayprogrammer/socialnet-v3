from typing import Union
from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.api.deps import get_current_socket_user
from app.api.sockets.base import BaseSocketConnectionManager
from app.models.accounts.tables import User
from app.models.profiles.tables import Notification

notification_socket_router = APIRouter()


class NotificationData(BaseModel):
    id: UUID
    status: str
    ntype: str


class NotificationSocketManager(BaseSocketConnectionManager):
    async def receive_data(self, websocket: WebSocket):
        data, err = await super().receive_data(websocket)
        if data != None:
            # Ensure data is a notification data. That means it align with the Notification data above
            try:
                NotificationData(**data)
            except Exception:
                err = "Invalid Notification data"
        return data, err

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            user = connection.socket_user
            if not user:
                continue
            user_is_among_receivers = await Notification.exists().where(
                Notification.receiver_ids.any(user.id), Notification.id == data["id"]
            )
            if user_is_among_receivers:
                # Only true receivers should access the data
                await connection.send_json(data)


manager = NotificationSocketManager()


@notification_socket_router.websocket("/api/v3/ws/notifications")
async def websocket_endpoint(
    websocket: WebSocket, user: Union[User, str] = Depends(get_current_socket_user)
):
    websocket.socket_user = (
        user if isinstance(user, User) else None
    )  # Attach user ID to webscoket
    await manager.connect(websocket)
    try:
        while True:
            data, err = await manager.receive_data(websocket)
            if err:
                await manager.send_error_data(websocket, err, 4000)
                break
            if isinstance(user, str):
                # in app connection (with socket secret)
                # Send data
                await manager.broadcast(data)
            else:
                await manager.send_error_data(
                    websocket, "Unauthorized to send data", 4001
                )
                break
    except WebSocketDisconnect:
        await manager.disconnect(websocket, True)

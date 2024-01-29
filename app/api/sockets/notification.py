from typing import Literal, Union
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketException,
)
from pydantic import BaseModel
from app.api.deps import get_current_socket_user
from app.api.sockets.base import BaseSocketConnectionManager
from app.common.handlers import ErrorCode
from app.models.accounts.tables import User
from app.models.profiles.tables import Notification

notification_socket_router = APIRouter()


class NotificationData(BaseModel):
    id: UUID
    status: Literal["CREATED", "DELETED"]
    ntype: str


class NotificationSocketManager(BaseSocketConnectionManager):
    async def receive_data(self, websocket: WebSocket):
        data = await super().receive_data(websocket)
        # Ensure data is a notification data. That means it align with the Notification data above
        try:
            NotificationData(**data)
        except Exception:
            await self.send_error_data(
                websocket, "Invalid Notification data", ErrorCode.INVALID_ENTRY
            )
        return data

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            user = connection.scope["user"]
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
    websocket.scope["user"] = (
        user if isinstance(user, User) else None
    )  # Attach user to webscoket
    await manager.connect(websocket)
    try:
        while True:
            data = await manager.receive_data(websocket)
            if isinstance(user, str):
                # in app connection (with socket secret)
                # Send data
                await manager.broadcast(data)
            else:
                await manager.send_error_data(
                    websocket, "Unauthorized to send data", ErrorCode.NOT_ALLOWED, 4001
                )
    except Exception as e:
        if websocket in manager.active_connections:
            manager.active_connections.remove(websocket)
        if isinstance(e, WebSocketException):
            await websocket.close()

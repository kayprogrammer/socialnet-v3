import json
from typing import Literal, Union
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketException,
)
from pydantic import BaseModel
import websockets
from app.api.deps import get_current_socket_user
from app.api.schemas.chat import MessageSchema
from app.api.sockets.base import BaseSocketConnectionManager
from app.common.handlers import ErrorCode
from app.core.config import settings
from app.models.accounts.tables import User
from app.models.chat.tables import Chat, Message
import os

chat_socket_router = APIRouter()


class SocketMessageSchema(BaseModel):
    status: Literal["CREATED", "UPDATED", "DELETED"]
    id: UUID


class ChatSocketManager(BaseSocketConnectionManager):
    async def connect(self, websocket: WebSocket, chat_id):
        # Verify chat ID & membership
        user = websocket.scope["user"]
        if user != settings.SOCKET_SECRET:
            await self.validate_chat_membership(websocket, chat_id)
        self.active_connections.append(websocket)

    async def validate_chat_membership(self, websocket: WebSocket, id: str):
        user = websocket.scope["user"]
        user_id = user.id
        chat, obj_user = await self.get_chat_or_user(websocket, user, id)
        if not chat and not obj_user:  # If no chat nor user
            await self.send_error_data(websocket, "Invalid ID", "invalid_input", 4004)

        if (
            chat and user_id not in chat.user_ids and user_id != chat.owner
        ):  # If chat but user is not a member
            await self.send_error_data(
                websocket, "You're not a member of this chat", "invalid_member", 4001
            )

    async def get_chat_or_user(self, websocket: WebSocket, user, id):
        chat, obj_user = None, None
        if user.id != id:
            chat = await Chat.objects().get(Chat.id == id)
            if not chat:
                # Probably a first DM message
                obj_user = await User.objects().get(User.username == id)
        else:
            obj_user = user  # Message is sent to self
        websocket.scope["obj_user"] = obj_user
        return chat, obj_user

    async def receive_data(self, websocket: WebSocket):
        data = await super().receive_data(websocket)
        # Ensure data is a Message data. That means it aligns with the Message schema above
        try:
            data = SocketMessageSchema(**data)
        except Exception:
            await self.send_error_data(
                websocket, "Invalid Message data", ErrorCode.INVALID_ENTRY, 4220
            )
        user = websocket.scope["user"]
        status = data.status
        if status == "DELETED" and user != settings.SOCKET_SECRET:
            await self.send_error_data(
                websocket,
                "Not allowed to send deletion socket",
                ErrorCode.UNAUTHORIZED_USER,
                4001,
            )

        message_data = {"id": str(data.id), "status": status}
        if status != "DELETED":
            message = await Message.objects(
                Message.sender, Message.sender.avatar, Message.file
            ).get(Message.id == data.id)
            if not message:
                await self.send_error_data(
                    websocket, "Invalid message ID", ErrorCode.NON_EXISTENT, 4004
                )
            elif message.sender.id != user.id:
                await self.send_error_data(
                    websocket, "Message isn't yours", ErrorCode.INVALID_OWNER, 4001
                )

            data = message_data | {
                "chat_id": str(message.chat),
                "created_at": str(message.created_at),
                "updated_at": str(message.updated_at),
            }
            message_data = data | MessageSchema.model_validate(message).model_dump(
                exclude={"id", "chat", "created_at", "updated_at"}, by_alias=True
            )
        return message_data

    async def broadcast(self, data: dict, group_name):
        for connection in self.active_connections:
            # Only true receivers should access the data
            if connection.scope["group_name"] == group_name:
                user = connection.scope["user"]
                obj_user = connection.scope.get("obj_user")
                if obj_user:
                    # Ensure that reading messages from a user id can only be done by the owner
                    if user == obj_user:
                        await connection.send_json(data)
                else:
                    await connection.send_json(data)


manager = ChatSocketManager()


@chat_socket_router.websocket("/api/v3/ws/chats/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: str,
    user: Union[User, str] = Depends(get_current_socket_user),
):
    websocket.scope["user"] = user
    try:
        while True:
            group_name = f"chat_{chat_id}"
            websocket.scope["group_name"] = group_name
            await manager.connect(websocket, chat_id)
            data = await manager.receive_data(websocket)
            await manager.broadcast(data, group_name)
    except Exception as e:
        if websocket in manager.active_connections:
            manager.active_connections.remove(websocket)
        if isinstance(e, WebSocketException):
            await websocket.close()


# Send message deletion details in websocket
async def send_message_deletion_in_socket(
    secured: bool, host: str, chat_id: UUID, message_id: UUID
):
    if os.environ.get("ENVIRONMENT") == "testing":
        return
    websocket_scheme = "wss://" if secured else "ws://"
    uri = f"{websocket_scheme}{host}/api/v3/ws/chats/{chat_id}"
    chat_data = {
        "id": str(message_id),
        "status": "DELETED",
    }
    headers = [
        ("Authorization", settings.SOCKET_SECRET),
    ]
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # Send the message to the WebSocket server
        await websocket.send(json.dumps(chat_data))
        await websocket.close()

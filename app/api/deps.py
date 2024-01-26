from typing import Union
from fastapi import Depends, WebSocket, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.api.utils.auth import Authentication
from app.common.handlers import ErrorCode, RequestError
from app.core.config import settings
from app.models.accounts.tables import User

jwt_scheme = HTTPBearer(auto_error=False)


async def get_user(token, socket: WebSocket = None):
    token = token if socket else token.credentials
    user = await Authentication.decodeAuthorization(token)
    if not user:
        err_msg = "Auth Token is Invalid or Expired!"
        if not socket:
            raise RequestError(
                err_code=ErrorCode.INVALID_TOKEN,
                err_msg=err_msg,
                status_code=401,
            )
        await socket.send_json(
            {
                "status": "error",
                "code": 4001,
                "message": err_msg,
            }
        )
        raise WebSocketException(code=4001, reason=err_msg)
    return user


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> User:
    if not token:
        raise RequestError(
            err_code=ErrorCode.UNAUTHORIZED_USER,
            err_msg="Unauthorized User!",
            status_code=401,
        )
    return await get_user(token)


async def get_current_user_or_guest(
    token: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> User:
    if not token:
        return None
    return await get_user(token)


async def get_current_socket_user(
    websocket: WebSocket,
) -> Union[User, str]:
    await websocket.accept()
    token = websocket.headers.get("authorization")
    # Return user or socket secret key
    if not token:
        err_msg = "Unauthorized User!"
        await websocket.send_json({"status": "error", "code": 4001, "message": err_msg})
        raise WebSocketException(code=4001, reason=err_msg)
    if token == settings.SOCKET_SECRET:
        return token
    return await get_user(token[7:], websocket)

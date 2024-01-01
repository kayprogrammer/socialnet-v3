from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.api.utils.auth import Authentication
from app.common.handlers import ErrorCode, RequestError
from app.models.accounts.tables import User

jwt_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_scheme),
) -> User:
    if not token:
        raise RequestError(
            err_code=ErrorCode.UNAUTHORIZED_USER,
            err_msg="Unauthorized User!",
            status_code=401,
        )
    user = await Authentication.decodeAuthorization(token.credentials)
    if not user:
        raise RequestError(
            err_code=ErrorCode.INVALID_TOKEN,
            err_msg="Auth Token is Invalid or Expired",
            status_code=401,
        )
    return user

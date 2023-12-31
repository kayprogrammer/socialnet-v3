from fastapi import APIRouter, BackgroundTasks
from app.common.handlers import ErrorCode

from app.api.schemas.base import ResponseSchema
from app.api.schemas.auth import (
    LoginUserSchema,
    RefreshTokensSchema,
    RegisterResponseSchema,
    RegisterUserSchema,
    RequestOtpSchema,
    SetNewPasswordSchema,
    TokensResponseSchema,
    VerifyOtpSchema,
)

from app.api.utils.emails import send_email

from app.models.accounts.tables import User

from app.common.handlers import RequestError

router = APIRouter()


@router.post(
    "/register",
    summary="Register a new user",
    description="This endpoint registers new users into our application",
    status_code=201,
)
async def register(
    background_tasks: BackgroundTasks, data: RegisterUserSchema
) -> RegisterResponseSchema:
    # Check for existing user
    existing_user = await User.objects().get(User.email == data.email)
    if existing_user:
        raise RequestError(
            err_code=ErrorCode.INVALID_ENTRY,
            err_msg="Invalid Entry",
            status_code=422,
            data={"email": "Email already registered!"},
        )

    # Create user
    user = await User.create_user(**data.model_dump())

    # Send verification email
    await send_email(background_tasks, user, "activate")
    return {"message": "Registration successful", "data": {"email": data.email}}

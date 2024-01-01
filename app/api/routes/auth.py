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

from app.models.accounts.tables import Otp, User

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


@router.post(
    "/verify-email",
    summary="Verify a user's email",
    description="This endpoint verifies a user's email",
    status_code=200,
)
async def verify_email(
    background_tasks: BackgroundTasks,
    data: VerifyOtpSchema,
) -> ResponseSchema:
    user_by_email = await User.objects().get(User.email == data.email)

    if not user_by_email:
        raise RequestError(
            err_code=ErrorCode.INCORRECT_EMAIL,
            err_msg="Incorrect Email",
            status_code=404,
        )

    if user_by_email.is_email_verified:
        return ResponseSchema(message="Email already verified")

    otp = await Otp.objects().get(Otp.user == user_by_email.id)
    if not otp or otp.code != data.otp:
        raise RequestError(
            err_code=ErrorCode.INCORRECT_OTP, err_msg="Incorrect Otp", status_code=404
        )
    if otp.check_expiration():
        raise RequestError(err_code=ErrorCode.EXPIRED_OTP, err_msg="Expired Otp")

    user_by_email.is_email_verified = True
    await user_by_email.save()
    await otp.remove()

    # Send welcome email
    await send_email(background_tasks, user_by_email, "welcome")
    return {"message": "Account verification successful"}

@router.post(
    "/resend-verification-email",
    summary="Resend Verification Email",
    description="This endpoint resends new otp to the user's email",
)
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    data: RequestOtpSchema,
) -> ResponseSchema:
    user_by_email = await User.objects().get(User.email == data.email)
    if not user_by_email:
        raise RequestError(err_msg="Incorrect Email", status_code=404)
    if user_by_email.is_email_verified:
        return {"message": "Email already verified"}

    # Send verification email
    await send_email(background_tasks, user_by_email, "activate")
    return {"message": "Verification email sent"}

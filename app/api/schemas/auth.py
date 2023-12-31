from pydantic import validator, Field, EmailStr, BaseModel
from .base import ResponseSchema
from .schema_examples import UserExample, token_example


class RegisterUserSchema(BaseModel):
    first_name: str = Field(..., example=UserExample.first_name)
    last_name: str = Field(..., example=UserExample.last_name)
    email: EmailStr = Field(..., example=UserExample.email)
    password: str = Field(..., example=UserExample.password)
    terms_agreement: bool

    @validator("first_name", "last_name")
    def validate_name(cls, v):
        if len(v.split(" ")) > 1:
            raise ValueError("No spacing allowed")
        elif len(v) > 50:
            raise ValueError("50 characters max")
        return v

    @validator("terms_agreement")
    def validate_terms_agreement(cls, v):
        if not v:
            raise ValueError("You must agree to terms and conditions")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("8 characters min!")
        return v


class VerifyOtpSchema(BaseModel):
    email: EmailStr = Field(..., example=UserExample.email)
    otp: int


class RequestOtpSchema(BaseModel):
    email: EmailStr = Field(..., example=UserExample.email)


class SetNewPasswordSchema(BaseModel):
    email: EmailStr = Field(..., example=UserExample.email)
    otp: int
    password: str = Field(..., example="newstrongpassword")

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("8 characters min!")
        return v


class LoginUserSchema(BaseModel):
    email: EmailStr = Field(..., example=UserExample.email)
    password: str = Field(..., example=UserExample.password)


class RefreshTokensSchema(BaseModel):
    refresh: str = Field(
        ...,
        example=token_example,
    )


class RegisterResponseSchema(ResponseSchema):
    data: RequestOtpSchema


class TokensResponseDataSchema(BaseModel):
    access: str = Field(
        ...,
        example=token_example,
    )
    refresh: str = Field(
        ...,
        example=token_example,
    )


class TokensResponseSchema(ResponseSchema):
    data: TokensResponseDataSchema

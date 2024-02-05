from fastapi_mail import ConnectionConfig
from pathlib import Path
from typing import List, Optional, Union

from pydantic import EmailStr, validator
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # DEBUG
    DEBUG: bool

    # TOKENS
    EMAIL_OTP_EXPIRE_SECONDS: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    # SECURITY
    SECRET_KEY: str
    SOCKET_SECRET: str

    # PROJECT DETAILS
    PROJECT_NAME: str
    FRONTEND_URL: str
    CORS_ALLOWED_ORIGINS: Union[List, str]
    ALLOWED_HOSTS: Union[List, str]

    # POSTGRESQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    # FIRST SUPERUSER
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # FIRST AUCTIONEER
    FIRST_CLIENT_EMAIL: EmailStr
    FIRST_CLIENT_PASSWORD: str

    # EMAIL CONFIG
    MAIL_SENDER_EMAIL: str
    MAIL_SENDER_PASSWORD: str
    MAIL_SENDER_HOST: str
    MAIL_SENDER_PORT: int
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: str
    TEMPLATE_FOLDER: Optional[str] = f"{PROJECT_DIR}/app/templates"

    EMAIL_CONFIG: Optional[ConnectionConfig] = None
    # CLOUDINARY CONFIG
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    @validator("CORS_ALLOWED_ORIGINS", "ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        return v.split()

    @validator("EMAIL_CONFIG", pre=True)
    def _assemble_email_config(cls, v: Optional[str], values):
        return ConnectionConfig(
            MAIL_USERNAME=values.get("MAIL_SENDER_EMAIL"),
            MAIL_PASSWORD=values.get("MAIL_SENDER_PASSWORD"),
            MAIL_FROM=values.get("MAIL_SENDER_EMAIL"),
            MAIL_PORT=values.get("MAIL_SENDER_PORT"),
            MAIL_SERVER=values.get("MAIL_SENDER_HOST"),
            MAIL_FROM_NAME=values.get("MAIL_FROM_NAME"),
            MAIL_STARTTLS=values.get("MAIL_STARTTLS"),
            MAIL_SSL_TLS=values.get("MAIL_SSL_TLS"),
            USE_CREDENTIALS=values.get("USE_CREDENTIALS"),
            TEMPLATE_FOLDER=values.get("TEMPLATE_FOLDER"),
        )

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings: Settings = Settings()

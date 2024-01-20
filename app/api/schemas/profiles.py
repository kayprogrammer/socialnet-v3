from typing import Any, Dict, List, Optional
from pydantic import EmailStr, validator, Field
from datetime import datetime, date
from .base import (
    BaseModel,
    PaginatedResponseDataSchema,
    ResponseSchema,
    UserDataSchema,
)
from .schema_examples import file_upload_data
from app.api.utils.file_processors import FileProcessor
from uuid import UUID

from app.api.utils.utils import validate_image_type


class CitySchema(BaseModel):
    id: UUID
    name: str
    region: str
    country: str


class CitiesResponseSchema(ResponseSchema):
    data: List[CitySchema]


class ProfileSchema(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    username: str = Field(..., example="john-doe")
    email: EmailStr = Field(..., example="johndoe@email.com")
    get_avatar: Optional[str] = Field(
        ..., example="https://img.com", serialization_alias="avatar"
    )
    bio: Optional[str] = Field(
        ..., example="Software Engineer | Django Ninja Developer"
    )
    dob: Optional[date]
    city_name: Optional[str] = Field(None, example="Lagos", serialization_alias="city")
    created_at: datetime
    updated_at: datetime


class ProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, example="John", max_length=50, min_length=1)
    last_name: Optional[str] = Field(None, example="Doe", max_length=50, min_length=1)
    bio: Optional[str] = Field(
        None,
        example="Software Engineer | Django Ninja Developer",
        max_length=200,
        min_length=1,
    )
    dob: Optional[date]
    city_id: Optional[UUID]
    file_type: Optional[str] = Field(None, example="image/jpeg")

    @validator("file_type")
    def validate_img_type(cls, v):
        return validate_image_type(v)


class DeleteUserSchema(BaseModel):
    password: str


class ProfilesResponseDataSchema(PaginatedResponseDataSchema):
    users: List[ProfileSchema] = Field(..., alias="items")


class ProfilesResponseSchema(ResponseSchema):
    data: ProfilesResponseDataSchema


class ProfileResponseSchema(ResponseSchema):
    data: ProfileSchema


class ProfileUpdateResponseDataSchema(ProfileSchema):
    get_avatar: Optional[Any] = Field(..., exclude=True, hidden=True)
    image_upload_id: Optional[Any] = Field(..., exclude=True, hidden=True)
    file_upload_data: Optional[Dict] = Field(None, example=file_upload_data)

    @validator("file_upload_data", always=True)
    def assemble_file_upload_data(cls, v, values):
        image_upload_id = values.get("image_upload_id")
        if image_upload_id:
            return FileProcessor.generate_file_signature(
                key=image_upload_id,
                folder="avatars",
            )
        return None


class ProfileUpdateResponseSchema(ResponseSchema):
    data: ProfileUpdateResponseDataSchema


class SendFriendRequestSchema(BaseModel):
    username: str


class AcceptFriendRequestSchema(SendFriendRequestSchema):
    accepted: bool


class NotificationSchema(BaseModel):
    id: UUID
    sender: Optional[UserDataSchema]
    ntype: str = Field(..., example="REACTION")
    message: str = Field(..., example="John Doe reacted to your post")
    post_slug: Optional[str]
    comment_slug: Optional[str]
    reply_slug: Optional[str]
    is_read: bool


class ReadNotificationSchema(BaseModel):
    mark_all_as_read: bool
    id: Optional[UUID] = None

    @validator("id", always=True)
    def validate_id(cls, v, values):
        if not v and not values["mark_all_as_read"]:
            raise ValueError("Set ID or mark all as read as True")
        return v


class NotificationsResponseDataSchema(PaginatedResponseDataSchema):
    notifications: List[NotificationSchema] = Field(..., alias="items")


class NotificationsResponseSchema(ResponseSchema):
    data: NotificationsResponseDataSchema

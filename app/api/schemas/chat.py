from typing import Any, Dict, List, Optional
from pydantic import Field, validator
from app.api.schemas.base import (
    BaseModel,
    PaginatedResponseDataSchema,
    ResponseSchema,
    UserDataSchema,
)
from uuid import UUID
from datetime import datetime
from app.api.utils.file_processors import FileProcessor
from .schema_examples import file_upload_data

from app.api.utils.utils import validate_file_type


class ChatSchema(BaseModel):
    id: UUID
    name: Optional[str]
    owner: UserDataSchema
    ctype: str
    description: Optional[str]
    get_image: Optional[str] = Field(..., serialization_alias="image")
    latest_message: Optional[dict]
    created_at: datetime
    updated_at: datetime


class MessageSchema(BaseModel):
    id: UUID
    chat: UUID = Field(..., serialization_alias="chat_id")
    sender: UserDataSchema
    text: Optional[str]
    get_file: Optional[str] = Field(..., serialization_alias="file")
    created_at: datetime
    updated_at: datetime


class MessageUpdateSchema(BaseModel):
    file_type: Optional[str] = Field(None, example="image/jpeg")
    text: Optional[str] = Field(None, example="Hello")

    @validator("text", always=True)
    def validate_text(cls, v, values):
        if not v and not values.get("file_type"):
            raise ValueError("You must enter a text")
        return v

    @validator("file_type", always=True)
    def validate_file_type(cls, v):
        return validate_file_type(v)


class MessageCreateSchema(MessageUpdateSchema):
    chat_id: Optional[UUID] = Field(None)
    username: Optional[str] = Field(None, example="john-doe")

    @validator("username", always=True)
    def validate_username(cls, v, values):
        chat_id = values.get("chat_id")
        if not chat_id and not v:
            raise ValueError("You must enter the recipient's username")
        elif chat_id and v:
            raise ValueError("Can't enter username when chat_id is set")
        return v


class MessagesResponseDataSchema(PaginatedResponseDataSchema):
    items: List[MessageSchema]


class MessagesSchema(BaseModel):
    chat: ChatSchema
    messages: MessagesResponseDataSchema
    users: List[UserDataSchema]


# RESPONSES
class ChatsResponseDataSchema(PaginatedResponseDataSchema):
    items: List[ChatSchema] = Field(..., serialization_alias="chats")


class ChatsResponseSchema(ResponseSchema):
    data: ChatsResponseDataSchema


class MessageCreateResponseDataSchema(MessageSchema):
    get_file: Optional[Any] = Field(None, exclude=True, hidden=True)
    file_upload_id: Optional[Any] = Field(..., exclude=True, hidden=True)
    file_upload_data: Optional[Dict] = Field(None, example=file_upload_data)

    @validator("file_upload_data", always=True)
    def assemble_file_upload_data(cls, v, values):
        file_upload_id = values.get("file_upload_id")
        if file_upload_id:
            return FileProcessor.generate_file_signature(
                key=file_upload_id,
                folder="messages",
            )
        return None


class MessageCreateResponseSchema(ResponseSchema):
    data: MessageCreateResponseDataSchema

class ChatResponseSchema(ResponseSchema):
    data: MessagesSchema
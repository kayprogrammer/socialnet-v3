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


# RESPONSES
class ChatsResponseDataSchema(PaginatedResponseDataSchema):
    items: List[ChatSchema] = Field(..., serialization_alias="chats")


class ChatsResponseSchema(ResponseSchema):
    data: ChatsResponseDataSchema

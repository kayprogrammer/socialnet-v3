from typing import Any, Optional
from pydantic import BaseModel as OriginalBaseModel, Field

from app.api.utils.file_processors import FileProcessor


class ResponseSchema(OriginalBaseModel):
    status: str = "success"
    message: str


class BaseModel(OriginalBaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True


class PaginatedResponseDataSchema(BaseModel):
    per_page: int
    current_page: int
    last_page: int


class UserDataSchema(BaseModel):
    full_name: str = Field(..., alias="name")
    username: str
    get_avatar: Optional[str] = Field(..., serialization_alias="avatar")

    @staticmethod
    def resolve_file_upload_data(obj):
        if obj.image_upload_status:
            return FileProcessor.generate_file_signature(
                key=obj.image.id,
                folder="posts",
            )
        return None

    # class Config:
    #     schema_extra = {"example": user}

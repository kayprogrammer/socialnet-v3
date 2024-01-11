from typing import Optional
from pydantic import BaseModel as OriginalBaseModel, Field
from .schema_examples import user_data


class ResponseSchema(OriginalBaseModel):
    status: str = "success"
    message: str


class BaseModel(OriginalBaseModel):
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
        populate_by_name = True

        @staticmethod
        def json_schema_extra(schema: dict, _):
            props = {}
            for k, v in schema.get("properties", {}).items():
                if not v.get("hidden", False):
                    props[k] = v
            schema["properties"] = props


class PaginatedResponseDataSchema(BaseModel):
    per_page: int
    current_page: int
    last_page: int


class UserDataSchema(BaseModel):
    full_name: str = Field(..., alias="name")
    username: str
    get_avatar: Optional[str] = Field(..., serialization_alias="avatar")

    class Config:
        json_schema_extra = {"example": user_data}

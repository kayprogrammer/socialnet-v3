from pydantic import BaseModel, Field


class ResponseSchema(BaseModel):
    status: str = "success"
    message: str

class PaginatedResponseDataSchema(BaseModel):
    per_page: int
    current_page: int
    last_page: int


class UserDataSchema(BaseModel):
    name: str = Field(..., alias="full_name")
    username: str
    avatar: str = Field(None, alias="get_avatar")

    # class Config:
    #     schema_extra = {"example": user}
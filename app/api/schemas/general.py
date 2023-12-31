from pydantic import BaseModel

from .base import ResponseSchema


# Site Details
class SiteDetailDataSchema(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    fb: str
    tw: str
    wh: str
    ig: str

    class Config:
        from_attributes = True


class SiteDetailResponseSchema(ResponseSchema):
    data: SiteDetailDataSchema

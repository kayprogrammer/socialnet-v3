from app.models.base.tables import BaseModel
from piccolo.columns import (
    Varchar,
    Email,
)


class SiteDetail(BaseModel):
    name = Varchar(300, default="SocialNet")
    email = Email(default="kayprogrammer1@gmail.com")
    phone = Varchar(300, default="+2348133831036")
    address = Varchar(300, default="234, Lagos, Nigeria")
    fb = Varchar(300, default="https://facebook.com")
    tw = Varchar(300, default="https://twitter.com")
    wh = Varchar(
        300,
        default="https://wa.me/2348133831036",
    )
    ig = Varchar(300, default="https://instagram.com")

    def __str__(self):
        return self.name

from app.db.models.base import BaseModel, File
from piccolo.columns import (
    Varchar,
    UUID,
    Timestamptz,
    Email,
    ForeignKey,
    OnDelete,
    Boolean,
    Date,
    Secret,
)


class City(BaseModel):
    name = Varchar(length=100)


class User(BaseModel, tablename="base_user"):
    first_name = Varchar(length=50)
    last_name = Varchar(length=50)
    username = Varchar(length=200)
    email = Email(unique=True)
    password = Secret(length=255)
    avatar = ForeignKey(references=File, on_delete=OnDelete.set_null, null=True)
    terms_agreement = Boolean(default=False)
    is_email_verified = Boolean(default=False)
    is_staff = Boolean(default=False)
    is_active = Boolean(default=True)

    # Profile Fields
    bio = Varchar(length=200, null=True)
    city = ForeignKey(references=City, on_delete=OnDelete.set_null, null=True)
    dob = Date(null=True)


from piccolo.apps.user.tables import BaseUser

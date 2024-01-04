import uuid
from datetime import datetime
from piccolo.table import Table
from piccolo.columns import UUID, Timestamptz, Varchar


class BaseModel(Table):
    id = UUID(default=uuid.uuid4, unique=True, primary_key=True)
    created_at = Timestamptz(default=datetime.now)
    updated_at = Timestamptz(auto_update=datetime.now)


class File(BaseModel):
    resource_type = Varchar(length=20)

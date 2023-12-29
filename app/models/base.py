import uuid
from datetime import datetime
from piccolo.table import Table
from piccolo.columns import UUID, Timestamptz


class BaseModel(Table):
    __abstract__ = True
    id = UUID(default=uuid.uuid4, unique=True)
    created_at = Timestamptz(default=datetime.now)
    updated_at = Timestamptz(default=datetime.now)

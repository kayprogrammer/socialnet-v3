from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import UUID
from piccolo.columns.defaults.uuid import UUID4


ID = "2024-01-27T16:48:12:415008"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="chat", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Chat",
        tablename="chat",
        column_name="latest_message_id",
        db_column_name="latest_message_id",
        params={"default": None},
        old_params={"default": UUID4()},
        column_class=UUID,
        old_column_class=UUID,
        schema=None,
    )

    return manager

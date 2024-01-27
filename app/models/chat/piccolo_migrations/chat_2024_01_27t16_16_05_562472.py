from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Array


ID = "2024-01-27T16:16:05:562472"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="chat", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Chat",
        tablename="chat",
        column_name="user_ids",
        db_column_name="user_ids",
        params={"null": True},
        old_params={"null": False},
        column_class=Array,
        old_column_class=Array,
        schema=None,
    )

    return manager

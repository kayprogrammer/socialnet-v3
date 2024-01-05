from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar


ID = "2024-01-05T13:00:26:145896"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="accounts", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="User",
        tablename="base_user",
        column_name="access_token",
        db_column_name="access_token",
        params={"null": True},
        old_params={"null": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    manager.alter_column(
        table_class_name="User",
        tablename="base_user",
        column_name="refresh_token",
        db_column_name="refresh_token",
        params={"null": True},
        old_params={"null": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager

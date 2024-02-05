from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2024-02-05T21:09:28:945786"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="accounts", description=DESCRIPTION
    )

    manager.rename_table(
        old_class_name="User",
        old_tablename="base_user",
        new_class_name="User",
        new_tablename="piccolo_user",
        schema=None,
    )

    return manager

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import BigInt
from piccolo.columns.column_types import SmallInt


ID = "2023-12-31T20:10:32:210177"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="user", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Otp",
        tablename="otp",
        column_name="code",
        db_column_name="code",
        params={},
        old_params={},
        column_class=BigInt,
        old_column_class=SmallInt,
        schema=None,
    )

    return manager

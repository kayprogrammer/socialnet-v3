from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2024-01-05T12:59:14:617308"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="accounts", description=DESCRIPTION
    )

    manager.drop_table(class_name="Jwt", tablename="jwt", schema=None)

    manager.add_column(
        table_class_name="User",
        tablename="base_user",
        column_name="access_token",
        db_column_name="access_token",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 1000,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="base_user",
        column_name="refresh_token",
        db_column_name="refresh_token",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 1000,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager

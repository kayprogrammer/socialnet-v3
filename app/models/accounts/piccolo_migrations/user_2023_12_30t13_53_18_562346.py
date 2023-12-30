from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import SmallInt
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import UUID
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.columns.defaults.uuid import UUID4
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class User(Table, tablename="base_user", schema=None):
    id = UUID(
        default=UUID4(),
        null=False,
        primary_key=True,
        unique=True,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


ID = "2023-12-30T13:53:18:562346"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="user", description=DESCRIPTION
    )

    manager.add_table(
        class_name="Jwt", tablename="jwt", schema=None, columns=None
    )

    manager.add_table(
        class_name="Otp", tablename="otp", schema=None, columns=None
    )

    manager.add_column(
        table_class_name="Jwt",
        tablename="jwt",
        column_name="refresh",
        db_column_name="refresh",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 1000,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Jwt",
        tablename="jwt",
        column_name="id",
        db_column_name="id",
        column_class_name="UUID",
        column_class=UUID,
        params={
            "default": UUID4(),
            "null": False,
            "primary_key": True,
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
        table_class_name="Jwt",
        tablename="jwt",
        column_name="created_at",
        db_column_name="created_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Jwt",
        tablename="jwt",
        column_name="updated_at",
        db_column_name="updated_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Jwt",
        tablename="jwt",
        column_name="user",
        db_column_name="user",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
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
        table_class_name="Jwt",
        tablename="jwt",
        column_name="access",
        db_column_name="access",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 1000,
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Otp",
        tablename="otp",
        column_name="id",
        db_column_name="id",
        column_class_name="UUID",
        column_class=UUID,
        params={
            "default": UUID4(),
            "null": False,
            "primary_key": True,
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
        table_class_name="Otp",
        tablename="otp",
        column_name="created_at",
        db_column_name="created_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Otp",
        tablename="otp",
        column_name="updated_at",
        db_column_name="updated_at",
        column_class_name="Timestamptz",
        column_class=Timestamptz,
        params={
            "default": TimestamptzNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Otp",
        tablename="otp",
        column_name="user",
        db_column_name="user",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
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
        table_class_name="Otp",
        tablename="otp",
        column_name="code",
        db_column_name="code",
        column_class_name="SmallInt",
        column_class=SmallInt,
        params={
            "default": 0,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager

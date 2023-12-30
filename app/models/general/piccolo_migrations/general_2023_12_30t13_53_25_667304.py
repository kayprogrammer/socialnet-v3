from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Email
from piccolo.columns.column_types import Timestamptz
from piccolo.columns.column_types import UUID
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.columns.defaults.uuid import UUID4
from piccolo.columns.indexes import IndexMethod


ID = "2023-12-30T13:53:25:667304"
VERSION = "1.2.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="general", description=DESCRIPTION
    )

    manager.add_table(
        class_name="SiteDetail",
        tablename="site_detail",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="SiteDetail",
        tablename="site_detail",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="name",
        db_column_name="name",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "SocialNet",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="email",
        db_column_name="email",
        column_class_name="Email",
        column_class=Email,
        params={
            "length": 255,
            "default": "kayprogrammer1@gmail.com",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="phone",
        db_column_name="phone",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "+2348133831036",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="address",
        db_column_name="address",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "234, Lagos, Nigeria",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="fb",
        db_column_name="fb",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "https://facebook.com",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="tw",
        db_column_name="tw",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "https://twitter.com",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="wh",
        db_column_name="wh",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "https://wa.me/2348133831036",
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
        table_class_name="SiteDetail",
        tablename="site_detail",
        column_name="ig",
        db_column_name="ig",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 300,
            "default": "https://instagram.com",
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

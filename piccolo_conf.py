from piccolo.engine.postgres import PostgresEngine
from piccolo.conf.apps import AppRegistry

from app.core.config import settings

DB = PostgresEngine(
    config={
        "host": settings.POSTGRES_SERVER,
        "database": settings.POSTGRES_DB,
        "user": settings.POSTGRES_USER,
        "password": settings.POSTGRES_PASSWORD,
        "port": settings.POSTGRES_PORT,
    },
    log_responses=True,
)

APP_REGISTRY = AppRegistry(
    apps=["app.models.base.piccolo_app", "app.models.general.piccolo_app", "app.models.accounts.piccolo_app", "app.models.feed.piccolo_app"]
)

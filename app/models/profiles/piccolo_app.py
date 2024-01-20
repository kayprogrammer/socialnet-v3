import os

from piccolo.conf.apps import AppConfig

from .tables import (
    Friend,
    Notification,
)

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="profiles",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=[
        Friend,
        Notification,
    ],
)

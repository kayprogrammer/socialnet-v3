import os

from piccolo.conf.apps import AppConfig

from .tables import Comment, Post, Reaction, Reply

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="feed",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=[Post, Comment, Reply, Reaction],
)

import os

from piccolo.conf.apps import AppConfig, Command

from .commands.change_password import change_password
from .commands.change_permissions import change_permissions
from .commands.create import create
from .tables import City, Country, Otp, Region, User

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="accounts",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=[Country, Region, City, User, Otp],
    migration_dependencies=[],
    commands=[
        Command(callable=create, aliases=["new"]),
        Command(callable=change_password, aliases=["password", "pass"]),
        Command(callable=change_permissions, aliases=["perm", "perms"]),
    ],
)

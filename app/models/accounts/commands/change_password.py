import sys

from piccolo.apps.user.commands.create import (
    get_confirmed_password,
    get_password,
    get_email,
)
from app.models.accounts.tables import User


def change_password():
    """
    Change a user's password.
    """
    email = get_email()
    password = get_password()
    confirmed_password = get_confirmed_password()

    if password != confirmed_password:
        sys.exit("Passwords don't match!")

    User.update_password_sync(user=email, password=password)

    print(f"Updated password for {email}")
    print(
        "If using session auth, we recommend invalidating this user's session."
    )

import typing as t
from app.models.accounts.tables import User
from piccolo.utils.warnings import Level, colored_string

if t.TYPE_CHECKING:  # pragma: no cover
    from piccolo.columns import Column


async def change_permissions(
    email: str,
    admin: t.Optional[bool] = None,
    superuser: t.Optional[bool] = None,
    active: t.Optional[bool] = None,
):
    """
    Change a user's permissions.

    :param username:
        Change the permissions for this user.
    :param admin:
        Set `admin` for the user (true / false).
    :param superuser:
        Set `superuser` for the user (true / false).
    :param active:
        Set `active` for the user (true / false).

    """
    if not await User.exists().where(User.email == email).run():
        print(
            colored_string(
                f"User {email} doesn't exist!", level=Level.medium
            )
        )
        return

    params: t.Dict[t.Union[Column, str], bool] = {}

    if admin is not None:
        params[User.admin] = admin

    if superuser is not None:
        params[User.superuser] = superuser

    if active is not None:
        params[User.active] = active

    if params:
        await User.update(params).where(
            User.email == email
        ).run()
    else:
        print(colored_string("No changes detected", level=Level.medium))
        return

    print(f"Updated permissions for {email}")

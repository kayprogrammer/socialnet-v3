from app.core.config import settings
from app.models.accounts.tables import User
from app.models.general.tables import SiteDetail
from piccolo.apps.user.tables import BaseUser


class CreateData(object):
    async def initialize(self) -> None:
        await self.create_superuser()
        await self.create_client()
        await self.create_sitedetail()

    async def create_superuser(self) -> None:
        superuser = await User.objects().get(
            User.email == settings.FIRST_SUPERUSER_EMAIL
        )
        user_dict = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "is_staff": True,
            "is_email_verified": True,
        }
        if not superuser:
            superuser = await User.create_user(**user_dict)

        # For piccolo admin
        username = "testadmin"
        piccolo_admin_superuser = (
            await BaseUser.objects()
            .where(
                (BaseUser.username == username)
                | (BaseUser.email == settings.FIRST_SUPERUSER_EMAIL)
            )
            .first()
        )
        if not piccolo_admin_superuser:
            superuser = await BaseUser.create_user(
                first_name=user_dict["first_name"],
                last_name=user_dict["last_name"],
                username=username,
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                active=True,
                superuser=True,
                admin=True,
            )
        return superuser

    async def create_client(self) -> None:
        client = await User.objects().get(User.email == settings.FIRST_CLIENT_EMAIL)
        user_dict = {
            "first_name": "Test",
            "last_name": "Client",
            "email": settings.FIRST_CLIENT_EMAIL,
            "password": settings.FIRST_CLIENT_PASSWORD,
            "is_email_verified": True,
        }
        if not client:
            client = await User.create_user(**user_dict)
        return client

    async def create_sitedetail(self) -> None:
        sitedetail = await SiteDetail.objects().first()
        if not sitedetail:
            sitedetail = await SiteDetail.objects().create()
        return sitedetail

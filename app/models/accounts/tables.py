from uuid import UUID

from slugify import slugify
from app.api.utils.utils import generate_random_alphanumeric_string
from app.core.config import settings
from app.models.base.tables import BaseModel, File
from piccolo.columns import (
    Varchar,
    Timestamptz,
    Email,
    ForeignKey,
    OnDelete,
    Boolean,
    Date,
    Secret,
    BigInt,
)
from piccolo.utils.sync import run_sync
from piccolo.columns.readable import Readable
from datetime import datetime
import logging
import typing as t
from argon2 import PasswordHasher
import random

logger = logging.getLogger(__name__)


class City(BaseModel):
    name = Varchar(length=100)


class User(BaseModel, tablename="base_user"):
    first_name = Varchar(length=50)
    last_name = Varchar(length=50)
    username = Varchar(length=200)
    email = Email(length=500, unique=True)
    password = Secret(length=255)
    avatar = ForeignKey(references=File, on_delete=OnDelete.set_null, null=True)
    terms_agreement = Boolean(default=False)
    active = Boolean(default=False)
    is_email_verified = Boolean(default=False)
    admin = Boolean(
        default=False, help_text="An admin can log into the Piccolo admin GUI."
    )
    superuser = Boolean(
        default=False,
        help_text=(
            "If True, this user can manage other users's passwords in the "
            "Piccolo admin GUI."
        ),
    )
    last_login = Timestamptz(
        null=True,
        default=None,
        required=False,
        help_text="When this user last logged in.",
    )

    # Tokens
    access_token = Varchar(1000, null=True)
    refresh_token = Varchar(1000, null=True)

    # Profile Fields
    bio = Varchar(length=200, null=True)
    city = ForeignKey(references=City, on_delete=OnDelete.set_null, null=True)
    dob = Date(null=True)

    _min_password_length = 6
    _max_password_length = 24
    _ph = PasswordHasher()

    @classmethod
    def get_readable(cls) -> Readable:
        """
        Used to get a readable string, representing a table row.
        """
        return Readable(template="%s", columns=[cls.email])

    ###########################################################################

    @classmethod
    def _validate_password(cls, password: str):
        """
        Validate the raw password. Used by :meth:`update_password` and
        :meth:`create_user`.

        :param password:
            The raw password e.g. ``'hello123'``.
        :raises ValueError:
            If the password fails any of the criteria.

        """
        if not password:
            raise ValueError("A password must be provided.")

        if len(password) < cls._min_password_length:
            raise ValueError("The password is too short.")

        if len(password) > cls._max_password_length:
            raise ValueError("The password is too long.")

    ###########################################################################

    @classmethod
    def update_password_sync(cls, user: t.Union[str, int], password: str):
        """
        A sync equivalent of :meth:`update_password`.
        """
        return run_sync(cls.update_password(user, password))

    @classmethod
    async def update_password(cls, user: t.Union[str, int], password: str):
        """
        The password is the raw password string e.g. ``'password123'``.
        The user can be a user ID, or a email.
        """
        if isinstance(user, str):
            clause = cls.email == user
        elif isinstance(user, UUID):
            clause = cls.id == user
        else:
            raise ValueError("The `user` arg must be a user id, or an email.")

        cls._validate_password(password=password)

        password = cls.hash_password(password)
        await cls.update({cls.password: password}).where(clause).run()

    ###########################################################################

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hashes the password, ready for storage, and for comparing during
        login.

        :raises ValueError:
            If an excessively long password is provided.

        """
        if len(password) > cls._max_password_length:
            logger.warning("Excessively long password provided.")
            raise ValueError("The password is too long.")
        hashed = cls._ph.hash(password)
        return hashed

    ###########################################################################

    @classmethod
    def login_sync(cls, email: str, password: str) -> t.Optional[int]:
        """
        A sync equivalent of :meth:`login`.
        """
        return run_sync(cls.login(email, password))

    @classmethod
    async def login(cls, email: str, password: str) -> t.Optional[int]:
        """
        Make sure the user exists and the password is valid. If so, the
        ``last_login`` value is updated in the database.

        :returns:
            The id of the user if a match is found, otherwise ``None``.

        """
        if len(email) > cls.email.length:
            logger.warning("Excessively long email provided.")
            return None

        if len(password) > cls._max_password_length:
            logger.warning("Excessively long password provided.")
            return None

        user = await cls.objects().get(cls.email == email)
        if not user:
            return None

        try:
            cls._ph.verify(user.password, password)
        except:
            return None

        user.last_login = datetime.now()
        await user.save()
        return user

    ###########################################################################

    @classmethod
    async def create_user(cls, email: str, password: str, **extra_params):
        """
        Creates a new user, and saves it in the database. It is recommended to
        use this rather than instantiating and saving ``User`` directly, as
        we add extra validation.

        :raises ValueError:
            If the email or password is invalid.
        :returns:
            The created ``User`` instance.

        """
        if not email:
            raise ValueError("An email must be provided.")

        cls._validate_password(password=password)
        password = cls.hash_password(password)
        user = cls(email=email, password=password, **extra_params)
        await user.save()
        return user

    async def save(self, *args, **kwargs):
        # Generate usename
        self.username = await self.generate_username()
        print(self.username)
        return await super().save(*args, **kwargs)

    async def generate_username(self):
        name = self.full_name
        username = self.username
        if name and (not username or not username.startswith(slugify(name))):
            # The if statement above implies that username will only be created or altered
            # if name exists and
            # if username is none OR name has changed (checking if the current username tallies with the name)

            unique_username = slugify(name)
            obj = (
                await User.objects()
                .where(User.username == unique_username, User.id != self.id)
                .first()
            )
            if obj:
                unique_username = (
                    f"{unique_username}-{generate_random_alphanumeric_string()}"
                )
                return await self.generate_username(unique_username)
            return unique_username
        return username

    @property
    def full_name(self):
        name = None
        first_name = self.first_name
        last_name = self.last_name
        if first_name and last_name:
            name = f"{self.first_name} {self.last_name}"
        return name


class Otp(BaseModel):
    user = ForeignKey(references=User, on_delete=OnDelete.cascade, unique=True)
    code = BigInt()

    def check_expiration(self):
        now = datetime.utcnow()
        diff = now - self.updated_at.replace(tzinfo=None)
        if diff.total_seconds() > settings.EMAIL_OTP_EXPIRE_SECONDS:
            return True
        return False

    @classmethod
    async def get_or_create(cls, user_id):
        code = random.randint(100000, 999999)
        otp = await cls.objects().get_or_create(
            cls.user == user_id, defaults={"code": code}
        )
        if not otp._was_created:
            otp.code = code
            await otp.save()
        return otp

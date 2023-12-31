from app.core.config import settings
from app.models.base.tables import BaseModel
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
import secrets
import logging
import typing as t
import hashlib
import random

logger = logging.getLogger(__name__)


class City(BaseModel):
    name = Varchar(length=100)


class File(BaseModel):
    resource_type = Varchar(length=20)


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

    # Profile Fields
    bio = Varchar(length=200, null=True)
    city = ForeignKey(references=City, on_delete=OnDelete.set_null, null=True)
    dob = Date(null=True)

    _min_password_length = 6
    _max_password_length = 128
    # The number of hash iterations recommended by OWASP:
    # https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pbkdf2
    _pbkdf2_iteration_count = 600_000

    def __init__(self, **kwargs):
        # Generating passwords upfront is expensive, so might need reworking.
        password = kwargs.get("password", None)
        if password:
            if not password.startswith("pbkdf2_sha256"):
                kwargs["password"] = self.__class__.hash_password(password)
        super().__init__(**kwargs)

    @classmethod
    def get_salt(cls):
        return secrets.token_hex(16)

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

        if password.startswith("pbkdf2_sha256"):
            logger.warning("Tried to create a user with an already hashed password.")
            raise ValueError("Do not pass a hashed password.")

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
        elif isinstance(user, int):
            clause = cls.id == user
        else:
            raise ValueError("The `user` arg must be a user id, or an email.")

        cls._validate_password(password=password)

        password = cls.hash_password(password)
        await cls.update({cls.password: password}).where(clause).run()

    ###########################################################################

    @classmethod
    def hash_password(
        cls, password: str, salt: str = "", iterations: t.Optional[int] = None
    ) -> str:
        """
        Hashes the password, ready for storage, and for comparing during
        login.

        :raises ValueError:
            If an excessively long password is provided.

        """
        if len(password) > cls._max_password_length:
            logger.warning("Excessively long password provided.")
            raise ValueError("The password is too long.")

        if not salt:
            salt = cls.get_salt()

        if iterations is None:
            iterations = cls._pbkdf2_iteration_count

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            bytes(password, encoding="utf-8"),
            bytes(salt, encoding="utf-8"),
            iterations,
        ).hex()
        return f"pbkdf2_sha256${iterations}${salt}${hashed}"

    def __setattr__(self, name: str, value: t.Any):
        """
        Make sure that if the password is set, it's stored in a hashed form.
        """
        if name == "password" and not value.startswith("pbkdf2_sha256"):
            value = self.__class__.hash_password(value)

        super().__setattr__(name, value)

    @classmethod
    def split_stored_password(cls, password: str) -> t.List[str]:
        elements = password.split("$")
        if len(elements) != 4:
            raise ValueError("Unable to split hashed password")
        return elements

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

        response = (
            await cls.select(cls._meta.primary_key, cls.password)
            .where(cls.email == email)
            .first()
            .run()
        )
        if not response:
            # No match found. We still call hash_password
            # here to mitigate the ability to enumerate
            # users via response timings
            cls.hash_password(password)
            return None

        stored_password = response["password"]

        algorithm, iterations_, salt, hashed = cls.split_stored_password(
            stored_password
        )
        iterations = int(iterations_)

        if cls.hash_password(password, salt, iterations) == stored_password:
            # If the password was hashed in an earlier Piccolo version, update
            # it so it's hashed with the currently recommended number of
            # iterations:
            if iterations != cls._pbkdf2_iteration_count:
                await cls.update_password(email, password)

            await cls.update({cls.last_login: datetime.now()}).where(cls.email == email)
            return response["id"]
        else:
            return None

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

        user = cls(email=email, password=password, **extra_params)
        await user.save()
        return user


class Jwt(BaseModel):
    user = ForeignKey(references=User, on_delete=OnDelete.cascade, unique=True)
    access = Varchar(1000)
    refresh = Varchar(1000)

    def __repr__(self):
        return f"Access - {self.access} | Refresh - {self.refresh}"


class Otp(BaseModel):
    user = ForeignKey(references=User, on_delete=OnDelete.cascade, unique=True)
    code = BigInt()

    def check_expiration(self):
        now = datetime.utcnow()
        diff = now - self.updated_at
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

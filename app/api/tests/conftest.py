from piccolo.engine.postgres import PostgresEngine
from piccolo.table import create_db_tables, drop_db_tables
from piccolo.conf.apps import Finder

from app.main import app
from app.api.utils.auth import Authentication
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from httpx import AsyncClient

from app.models.accounts.tables import City, Country, Region, User
from app.models.base.tables import File
from app.models.chat.tables import Chat, Message
from app.models.feed.tables import Comment, Post, Reaction, Reply
import pytest, asyncio, os

from app.models.profiles.tables import Friend

os.environ["ENVIRONMENT"] = "testing"
test_db = factories.postgresql_proc(port=None, dbname="test_db")
TABLES = Finder().get_table_classes()


# GENERAL FIXTURES
@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database(test_db):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password

    with DatabaseJanitor(
        pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        DB = PostgresEngine(
            config={
                "host": pg_host,
                "database": pg_db,
                "user": pg_user,
                "password": pg_password,
                "port": pg_port,
            },
        )
        yield DB


@pytest.fixture(autouse=True)
async def setup_db(database, mocker):
    mocker.patch("app.piccolo_conf.DB", new=database)
    await create_db_tables(*TABLES)
    yield
    await drop_db_tables(*TABLES)


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# -------------------------------------------------------------------------------


# AUTH FIXTURES
@pytest.fixture
async def test_user():
    user_dict = {
        "first_name": "Test",
        "last_name": "Name",
        "email": "test@example.com",
        "password": "testpassword",
    }
    user = await User.create_user(**user_dict)
    return user


@pytest.fixture
async def verified_user():
    user_dict = {
        "first_name": "Test",
        "last_name": "Verified",
        "email": "testverifieduser@example.com",
        "password": "testpassword",
        "is_email_verified": True,
    }
    user = await User.create_user(**user_dict)
    return user


@pytest.fixture
async def another_verified_user():
    user_dict = {
        "first_name": "AnotherTest",
        "last_name": "UserVerified",
        "email": "anothertestverifieduser@example.com",
        "password": "anothertestveuser",
        "is_email_verified": True,
    }

    user = await User.create_user(**user_dict)
    return user


@pytest.fixture
async def authorized_client(verified_user: User, client):
    access = await Authentication.create_access_token(
        {"user_id": str(verified_user.id), "username": verified_user.username}
    )
    refresh = await Authentication.create_refresh_token()
    verified_user.access_token = access
    verified_user.refresh_token = refresh
    await verified_user.save()
    client.headers = {**client.headers, "Authorization": f"Bearer {access}"}
    return client


@pytest.fixture
async def another_verified_user_tokens(another_verified_user: User):
    access = await Authentication.create_access_token(
        {
            "user_id": str(another_verified_user.id),
            "username": another_verified_user.username,
        }
    )
    refresh = await Authentication.create_refresh_token()
    another_verified_user.access_token = access
    another_verified_user.refresh_token = refresh
    await another_verified_user.save()
    return {"access": access, "refresh": refresh}


@pytest.fixture
async def another_authorized_client(another_verified_user_tokens, client):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {another_verified_user_tokens['access']}",
    }
    return client


# -------------------------------------------------------------------------------


# FEED FIXTURES
@pytest.fixture
async def post(verified_user):
    # Create Post
    post = await Post.objects().create(
        author=verified_user, text="This is a nice new platform"
    )
    return post


@pytest.fixture
async def reaction(post):
    # Create Reaction
    author = post.author
    reaction = await Reaction.objects().create(user=author, rtype="LIKE", post=post)
    return reaction


@pytest.fixture
async def comment(post):
    # Create Comment
    author = post.author
    comment = await Comment.objects().create(
        author=author, text="Just a comment", post=post
    )
    return comment


@pytest.fixture
async def reply(comment):
    # Create Reply
    author = comment.author
    reply = await Reply.objects().create(
        author=author, text="Simple reply", comment=comment
    )
    return reply


# -------------------------------------------------------------------------------


# PROFILE FIXTURES
@pytest.fixture
async def city():
    country = await Country.objects().create(name="TestCountry", code="TC")
    region = await Region.objects().create(name="TestRegion", country=country)
    city = await City.objects().create(name="TestCity", region=region, country=country)
    return city


@pytest.fixture
async def friend(verified_user: User, another_verified_user: User):
    friend = await Friend.objects().create(
        requester=verified_user,
        requestee=another_verified_user,
        status="ACCEPTED",
    )
    return friend


# -------------------------------------------------------------------------------


# CHAT FIXTURES
@pytest.fixture
async def chat(verified_user, another_verified_user):
    # Create Chat
    chat = await Chat.objects().create(
        owner=verified_user, user_ids=[another_verified_user.id]
    )
    return chat


@pytest.fixture
async def group_chat(verified_user, another_verified_user):
    # Create Group Chat
    chat = await Chat.objects().create(
        owner=verified_user,
        user_ids=[another_verified_user.id],
        name="My New Group",
        ctype="GROUP",
        description="This is the description of my group chat",
    )
    return chat


@pytest.fixture
async def message(chat):
    # Create Message
    message = await Message.objects().create(
        chat=chat, sender=chat.owner, text="Hello Boss"
    )
    return message


# -------------------------------------------------------------------------------

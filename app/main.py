from fastapi import FastAPI
from contextlib import asynccontextmanager
from piccolo.engine import engine_finder
from starlette.middleware.cors import CORSMiddleware

from app.api.routers import main_router
from app.api.sockets.notification import notification_socket_router
from app.api.sockets.chat import chat_socket_router
from app.common.handlers import exc_handlers
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open Database connection pool
    engine = engine_finder()
    await engine.start_connection_pool()
    yield
    # Close Database connection pool
    await engine.close_connection_pool()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="3.0.0",
    description="""
        A simple Social Networking API built with FastAPI & Piccolo ORM

        WEBSOCKETS:
            Notifications: 
                URL: wss://{host}/api/v3/ws/notifications
                * Requires authorization, so pass in the Bearer Authorization header.
                * You can only read and not send notification messages into this socket.
            Chats:
                URL: wss://{host}/api/v3/ws/chats/{id}
                * Requires authorization, so pass in the Bearer Authorization header.
                * Use chat_id as the ID for existing chat or username if its the first message in a DM.
                * You cannot read realtime messages from a username that doesn't belong to the authorized user, but you can surely send messages
                * Only send message to the socket endpoint after the message has been created or updated, and files has been uploaded.
                * Fields when sending message through the socket: e.g {"status": "CREATED", "id": "fe4e0235-80fc-4c94-b15e-3da63226f8ab"}
                    * status - This must be either CREATED or UPDATED (string type)
                    * id - This is the ID of the message (uuid type)
    """,
    openapi_url=f"/openapi.json",
    docs_url="/",
    security=[{"BearerToken": []}],
    exception_handlers=exc_handlers,
    lifespan=lifespan,
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "x-requested-with",
        "content-type",
        "accept",
        "origin",
        "authorization",
        "accept-encoding",
        "access-control-allow-origin",
        "content-disposition",
    ],
)

app.include_router(main_router, prefix="/api/v3")
app.add_websocket_route("/api/v3/ws/notifications", notification_socket_router)
app.add_websocket_route("/api/v3/ws/chats/{chat_id}", chat_socket_router)


@app.get("/api/v3/healthcheck", name="Healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"success": "pong!"}

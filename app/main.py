from fastapi import FastAPI
from contextlib import asynccontextmanager
from piccolo.engine import engine_finder
from starlette.middleware.cors import CORSMiddleware

from app.api.routers import main_router
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
    description="A simple Social Networking API built with FastAPI & Piccolo ORM",
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


@app.get("/api/v3/healthcheck", name="Healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"success": "pong!"}

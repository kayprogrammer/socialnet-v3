from piccolo.engine import engine_finder
from starlette.applications import Starlette


app = Starlette()


@app.on_event("startup")
async def open_database_connection_pool():
    engine = engine_finder()
    await engine.start_connection_pool()


@app.on_event("shutdown")
async def close_database_connection_pool():
    engine = engine_finder()
    await engine.close_connection_pool()

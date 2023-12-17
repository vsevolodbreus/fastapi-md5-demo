from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import session_manager
from .routers import api as api_router
from .routers import main as main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    session_manager.init(settings.POSTGRES_DB_URL_ASYNC)
    yield
    if session_manager._engine is not None:
        await session_manager.close()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router.router)
app.include_router(main_router.router)

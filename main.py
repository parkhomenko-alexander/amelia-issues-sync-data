from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from config import config

from app.db import (
    Base, db, Building, Company, 
    Facility, Floor, Issue, 
    Priority, RoomTechPassports, 
    Room, Service, Status, 
    StatusHistory, User, WorkCategory, Workflow
)

from app.api_v1 import router as router_v1

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db.engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    lifespan=lifespan,
    root_path=config.APPLICATION_PREFIX_BEHIND_PROXY,
)

app.include_router(router=router_v1)
# app.include_router(router=router_v1, prefix=config.api_v1_prefix)


if __name__ == '__main__':
    uvicorn.run(
        'main:app', 
        host=config.APPLICATION_HOST, 
        port=config.APPLICATION_PORT, 
        log_level=config.APPLICATION_LOG_LEVEL, 
        reload=config.APPLICATION_DEBUG
    )
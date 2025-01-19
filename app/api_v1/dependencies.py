from typing import Annotated

from fastapi import Depends

from app.utils.redis_manager import RedisManager
from app.utils.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork

UowDep = Annotated[
    AbstractUnitOfWork, 
    Depends(SqlAlchemyUnitOfWork)
]


def get_redis_manager():
    return RedisManager()

RedisManagerDep = Annotated[
    RedisManager,
    Depends(get_redis_manager)
]
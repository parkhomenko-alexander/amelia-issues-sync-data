from typing import Annotated

from fastapi import Depends

from app.services.permission.system_user_service import SystemUserService
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



def get_user_service_dep():
    return SystemUserService(SqlAlchemyUnitOfWork())

SystemUserServiceDep = Annotated[
    SystemUserService,
    Depends(get_user_service_dep)
]
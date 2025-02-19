from typing import Annotated

from fastapi import Depends
from app.services.permission.auth_service import AuthService
from app.services.permission.permission_service import PermissionService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork


def get_auth_service_dep():
    return AuthService(SqlAlchemyUnitOfWork())

AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service_dep)
]


def get_permission_service_dep():
    return PermissionService(SqlAlchemyUnitOfWork())

PermissionDep = Annotated[
    PermissionService,
    Depends(get_permission_service_dep)
]
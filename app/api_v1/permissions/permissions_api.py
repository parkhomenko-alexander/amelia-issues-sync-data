
from fastapi import APIRouter

from app.api_v1.dependencies import UowDep
from app.schemas.user_permission.system_user_schemas import SystemUserGetSchema, SystemUserPostSchema
from app.services.permission.system_user_service import SystemUserService
 
router = APIRouter(
    tags=['Permissions']
)

@router.get(
    '',
)
async def get_users(
):
    try:
        ...
    except Exception:
        ...

@router.get(
    '/me',
)
async def get_user_me(
):
    try:
        ...
    except Exception:
        ...

@router.post(
    '',
    response_model=SystemUserGetSchema
)
async def create_user(
    user: SystemUserPostSchema,
    uow: UowDep
):
    try:
        service = SystemUserService(uow)
        new_user = await service.create_user(user)
        return new_user
    except Exception:
        ...
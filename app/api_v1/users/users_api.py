
from fastapi import APIRouter, HTTPException

from app.api_v1.dependencies import UowDep
from app.schemas.user_permission.system_user_schemas import SystemUserGetSchema, SystemUserPostSchema
from app.services.permission.system_user_service import SystemUserService
 
router = APIRouter(
    tags=['Users']
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
        return await service.create_user(user)
    except Exception as er:
        raise HTTPException(status_code=500, detail={"error": f"Some error: {er}"})
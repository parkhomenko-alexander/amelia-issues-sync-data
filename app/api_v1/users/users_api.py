
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from app.api_v1.auth_validators import get_current_active_user
from app.api_v1.dependencies import SystemUserServiceDep, UowDep
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
    current_user: Annotated[SystemUserGetSchema, Depends(get_current_active_user)]
):
    try:
        return current_user
    except Exception:
        ...
 
@router.post(
    '',
    response_model=SystemUserGetSchema
)
async def create_user(
    user: SystemUserPostSchema,
    user_service: SystemUserServiceDep,
    # current_user: Annotated[SystemUserGetSchema, Depends(get_current_active_user)]
):
    try:
        # if current_user.role != "admin":
        #     raise HTTPException(status_code=403, detail={"error": f"Some error: Bad permission"})
        return await user_service.create_user(user)
    except Exception as er:
        raise HTTPException(status_code=500, detail={"error": f"Some error: {er}"})
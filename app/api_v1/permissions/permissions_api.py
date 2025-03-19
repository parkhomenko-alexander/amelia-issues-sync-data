
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
async def mock(
):
    try:
        ...
    except Exception:
        ...

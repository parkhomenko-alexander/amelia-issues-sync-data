from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

from app.api_v1.auth.dependencies import AuthServiceDep, PermissionDep
from app.schemas.user_permission.auth_schemas import TokenSchema
from app.api_v1.auth_validators import get_current_auth_user_for_refresh
from app.schemas.user_permission.system_user_schemas import SystemUserGetSchema


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    tags=['Auth'],
    dependencies=[Depends(http_bearer)],
)



@router.post(
    '',
    response_model=TokenSchema
)
async def authentificate(
    auth_service: AuthServiceDep,
    permission_service: PermissionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    finded_user = await auth_service.authentificate_user(form_data.username, form_data.password)
    role = await permission_service.translate_role_id_str(finded_user.role_id)
    access_token = auth_service.create_access_token(form_data.username, role)
    refresh_token = auth_service.create_refresh_token(form_data.username)
    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post(
    "/refresh",
    response_model=TokenSchema,
    response_model_exclude_none=True
)
def auth_refresh_jwt(
    auth_service: AuthServiceDep,
    user: SystemUserGetSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = auth_service.create_access_token(user.login, user.role)
    return TokenSchema(
        access_token=access_token
    )
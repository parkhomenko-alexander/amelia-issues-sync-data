from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.api_v1.auth.dependencies import AuthServiceDep, PermissionDep
from app.schemas.user_permission.auth_schemas import ShortUserSchema, TokenSchema
 
router = APIRouter(
    tags=['Auth']
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

@router.post(
    '',
    response_model=TokenSchema
)
async def authentificate(
    # user: ShortUserSchema,
    auth_service: AuthServiceDep,
    permission_service: PermissionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        user = ShortUserSchema(login=form_data.username, password=form_data.password)
        finded_user = await auth_service.authentificate_user(user.login, user.password)
        role = await permission_service.translate_role_id_str(finded_user.role_id)
        access_token = auth_service.create_access_token(user, role)
        refresh_token = auth_service.create_refresh_token(user)
        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    except Exception as er:
        raise HTTPException(status_code=500, detail={"error": f"Some error: {er}"})

# @router.get("/users/me/")
# def auth_user_check_self_info(
#     payload: dict = Depends(get_current_token_payload),
#     # user: UserSchema = Depends(get_current_active_auth_user),
# ):
#     iat = payload.get("iat")
#     return {
#         # "username": user.username,
#         # "email": user.email,
#         "logged_in_at": iat,
#     }

from typing import Annotated, Any, Awaitable, Callable, Coroutine

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.api_v1.auth.dependencies import AuthServiceDep
from app.api_v1.dependencies import SystemUserServiceDep, get_user_service_dep
from app.schemas.user_permission.auth_schemas import TokenData, TokenSchema
from app.schemas.user_permission.system_user_schemas import SystemUserGetSchema
from app.services.permission.auth_service import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_KEY
from config import config 
from loguru import logger

from jwt.exceptions import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=config.APPLICATION_PREFIX_BEHIND_PROXY + "/api/v1/auth",
)


def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> dict: 
    try:
        payload = auth_service.decode_token(token, config.APPLICATION_SECRET_KEY, algorithm=config.APPLICATION_HASH_ALGORITHM)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload


def validate_token_type(
    payload: dict,
    token_type: str
):
    payload_token_type = payload.get(TOKEN_TYPE_KEY)
    if token_type == payload_token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token type {token_type!r}"
    )


async def get_current_user(
    payload: dict,
    user_service: SystemUserServiceDep = get_user_service_dep()
) -> SystemUserGetSchema:
    error_resp = "Error in auth process"
    headers={"WWW-Authenticate": "Bearer"}
    try:
        login = payload.get("login")

        if login is None:
            logger.error(error_resp)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_resp,
                headers=headers
            )

        token_data = TokenData(login=login)
    except InvalidTokenError:
        logger.error(error_resp)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_resp,
            headers=headers
        )
    user = await user_service.get_user(login=token_data.login)
    if user is None:
        logger.error(error_resp)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_resp,
            headers=headers
        )
    return user


def get_current_user_by_token_type(
    token_type: str,
) -> Callable[..., Coroutine[Any, Any, SystemUserGetSchema]]:
    async def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
    ) -> SystemUserGetSchema:
        validate_token_type(payload, token_type)
        return await get_current_user(payload)
    return get_auth_user_from_token

get_current_auth_user = get_current_user_by_token_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_current_user_by_token_type(REFRESH_TOKEN_TYPE)


async def get_current_active_user(
    current_user: SystemUserGetSchema = Depends(get_current_auth_user),
):
    if current_user.is_disabled:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


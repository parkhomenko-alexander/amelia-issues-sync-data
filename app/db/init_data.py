import asyncio

from app.schemas.user_permission.roles_schemas import RolePostSchema
from app.schemas.user_permission.system_user_schemas import SystemUserPostSchema
from app.services.permission.permission_service import PermissionService
from app.services.permission.system_user_service import SystemUserService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork

from loguru import logger

import json
from config import config

async def create_roles(role_service: PermissionService, roles: list[dict] = []):

    try:
        for r in roles:
            await role_service.create_role(RolePostSchema(**r))
    except Exception as er:
        logger.error(f"Error role inserting. {er}")

async def create_users(user_service: SystemUserService, role_service: PermissionService, users: list[dict] = []):

    try:
        for u in users:
            role_id = await role_service.translate_role_str_id(u["role_title"])
            u.pop("role_title")
            u["role_id"] = role_id
            await user_service.create_user(SystemUserPostSchema(**u))
    except Exception as er:
        logger.error(f"Error role inserting. {er}")

def load_data(path: str = config.APPLICATION_INIT_DB_DATA_PATH, filename: str = config.APPLICATION_INIT_DB_DATA_FILENAME):
    with open(path+filename, "r", encoding="utf-8") as f_json_data:
        data: dict [str, list[dict]] = json.load(f_json_data)
        return data

async def init_data_db():
    uow = SqlAlchemyUnitOfWork()

    role_service = PermissionService(uow)
    user_service = SystemUserService(uow)

    try:
        data = load_data()
        await create_roles(role_service, data["roles"])
        await create_users(user_service, role_service, data["users"])
    except Exception as er:
        logger.error(f"Error role inserting. {er}")

asyncio.run(init_data_db())
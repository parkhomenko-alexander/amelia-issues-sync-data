import asyncio
from app.schemas.user_permission.roles_schemas import RolePostSchema
from app.services.permission.permission_service import PermissionService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork

from loguru import logger

roles = [RolePostSchema(title="user"), RolePostSchema(title="admin")]


async def create_roles(roles: list[RolePostSchema] = roles):
    uow = SqlAlchemyUnitOfWork()
    role_service = PermissionService(uow)

    try:
        for r in roles:
            await role_service.create_role(r)
    except Exception as er:
        logger.error(f"Error role inserting. {er}")

async def load_init_data():
    await create_roles()

asyncio.run(load_init_data())
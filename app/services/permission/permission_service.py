# from app.schemas.user_permission.roles_schemas import 
from app.schemas.user_permission.roles_schemas import RoleGetSchema, RolePostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork

from loguru import logger


class PermissionService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @with_uow
    async def create_role(self, role: RolePostSchema):
        existed_role = await self.uow.role_repo.find_one(title=role.title)

        if existed_role:
            resp = f"Role '{role.title}' exits"
            logger.info(resp)
            raise Exception(resp)
        else:
            dumped_role = role.model_dump()
            new_role = await self.uow.role_repo.add_one(dumped_role)
            if not new_role:
                raise Exception("New role not created")
            logger.info(f"Role {role.title} was added")
            await self.uow.commit()
            return RoleGetSchema.model_validate(new_role)
    
    @with_uow
    async def translate_role_id_str(self, role_id: int) -> str:
        role = await self.uow.role_repo.find_one(id=role_id)
        if not role:
            raise Exception(f"Role {role_id} not found")
        else:
            return role.title
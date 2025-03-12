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
        else:
            dumped_role = role.model_dump()
            new_role = await self.uow.role_repo.add_one(dumped_role)
            if not new_role:
                raise Exception("New role not created")
            logger.info(f"Role {role.title} was added")
            await self.uow.commit()
            return RoleGetSchema.model_validate(new_role)

    @with_uow
    async def get_role(self, **filters) -> RoleGetSchema:
        role = await self.uow.role_repo.find_one(**filters)
        if not role:
            raise ValueError(f"Role not found with filters: {filters}!r")
        return RoleGetSchema(title=role.title, id=role.id)
    
    @with_uow
    async def translate_role_id_str(self, role_id: int) -> str:
        role = await self.get_role(id=role_id)
        return role.title

    @with_uow
    async def translate_role_str_id(self, role_title: str) -> int:
        role = await self.get_role(title=role_title)
        return role.id

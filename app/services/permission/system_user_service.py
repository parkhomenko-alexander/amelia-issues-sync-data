from app.schemas.user_permission.system_user_schemas import SystemUserGetSchema, SystemUserPostSchema
from app.services.permission.auth_service import AuthService
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork

from loguru import logger



class SystemUserService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @with_uow
    async def create_user(self, user: SystemUserPostSchema, role: str = "user") -> SystemUserGetSchema:
        pas = AuthService._gen_password_hash(user.password)
        role_id = 10
        user.password = pas
        user.role_id = role_id
        dumped_user = user.model_dump(exclude={"password"})
        dumped_user["password_hash"] = pas

        existed_user = await self.uow.system_user_repo.find_one()

        if existed_user:
            resp = f"User '{user.login}' exists"
            logger.info(resp)
            raise Exception(resp)
        else:
            new_user = await self.uow.system_user_repo.add_one(dumped_user)
            if not new_user:
                raise Exception("New user not created")
            logger.info(f"User {user.login} was created")
            await self.uow.commit()
            return SystemUserGetSchema.model_validate(new_user)



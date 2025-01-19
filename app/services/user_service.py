from typing import Set
from loguru import logger
from app.schemas.user_schemas import UserPostSchema 
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class UserService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, elements_post: list[UserPostSchema]) -> int:
        """
        Users inserting
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.users_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Users between {elements_post[0].external_id}-{elements_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, elements_update: list[UserPostSchema]) -> int:
        """
        Users updating
        """
        elements_data_for_updating = [e.model_dump() for e in elements_update]
        try:
            await self.uow.users_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Users between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.users_repo.get_existing_external_ids(ids)

    @staticmethod
    async def get_fullname_id_mapping_by_roles(uow: AbstractUnitOfWork, roles: list[str]) -> dict[str, int]:
        async with uow:
            filter_by = uow.users_repo.create_roles_condition(roles)

            res = await uow.users_repo.get_all_fitered_or(filter_by)
            mapping = {}
            for u in res:
                mapping[f"{u.last_name} {u.first_name} {u.middle_name}"] = u.id

        return mapping

    @staticmethod
    async def get_users_ids(uow: AbstractUnitOfWork) -> Set[int]:
        async with uow:
            ids: set[int] = set()

            users = await uow.users_repo.get_all() 

            for u in users:
                ids.add(u.id)

        return ids

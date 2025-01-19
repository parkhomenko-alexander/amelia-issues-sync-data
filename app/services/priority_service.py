from loguru import logger
from app.schemas.priority_schemas import PriorityPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class PriorityService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow: AbstractUnitOfWork = uow

    # async def insert(self, priority_post: PriorityPostSchema) -> int:
    #     """
    #     Insert priority
    #     """
        
    #     external_id = priority_post.external_id

    #     facility =  await self.uow.priority_repo.find_one(external_id=external_id)
    #     new_facility = priority_post.model_dump()
    #     if facility:
    #         facility_id = await self.uow.priority_repo.edit_one(facility.id, new_facility)
    #     else:            
    #         facility_id = await self.uow.priority_repo.add_one(new_facility)
    #     await self.uow.commit()
    #     return facility_id
        
    @with_uow
    async def bulk_insert(self, priorities_post: list[PriorityPostSchema]) -> int:
        """
        Insert priority
        """
        priorities_data_for_inserting = [priority.model_dump() for priority in priorities_post]
        try:
            await self.uow.priority_repo.bulk_insert(priorities_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Priorities between {priorities_post[0].external_id}-{priorities_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, priorities_update: list[PriorityPostSchema]) -> int:
        """
        Insert priority
        """
        priority_data_for_updating = [priority.model_dump() for priority in priorities_update]
        try:
            await self.uow.priority_repo.bulk_update_by_external_ids(priority_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Facilites between {priorities_update[0].external_id}-{priorities_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.priority_repo.get_existing_external_ids(ids)

    @staticmethod    
    async def get_title_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            priorities = await uow.priority_repo.get_all()
            mapping: dict[str, int] = {}
            for pr in priorities:
                mapping[pr.title] = pr.id
            return mapping
        


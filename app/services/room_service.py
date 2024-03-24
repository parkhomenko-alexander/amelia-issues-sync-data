from loguru import logger
from app.schemas.room_schemas import RoomPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class RoomService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, elements_post: list[RoomPostSchema]) -> int:
        """
        Rooms inserting
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.room_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Rooms between {elements_post[0].external_id}-{elements_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, elements_update: list[RoomPostSchema]) -> int:
        """
        Rooms updating
        """
        elements_data_for_updating = [e.model_dump() for e in elements_update]
        try:
            await self.uow.room_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Rooms between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.room_repo.get_existing_external_ids(ids)


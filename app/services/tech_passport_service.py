from loguru import logger
from app.schemas.tech_passport_schemas import TechPassportPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class TechPassportService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, elements_post: list[TechPassportPostSchema]) -> int:
        """
        Tech passport inserting
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.tech_passport_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Tech passports in count {len(elements_data_for_inserting)} were inserted")
        return 0
    
    @with_uow
    async def bulk_update(self, elements_update: list[TechPassportPostSchema]) -> int:
        """
        Tech passport updating
        """
        elements_data_for_updating = [e.model_dump() for e in elements_update]
        try:
            await self.uow.tech_passport_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Rooms between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.tech_passport_repo.get_existing_external_ids(ids)                
              
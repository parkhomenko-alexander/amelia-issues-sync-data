from loguru import logger
from app.schemas.tech_passport_schemas import TechPassportSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class TechPassportService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, elements_post: list[TechPassportSchema]) -> int:
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
              
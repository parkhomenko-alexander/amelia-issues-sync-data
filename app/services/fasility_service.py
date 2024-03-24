from loguru import logger
from app.schemas.facility_schemas import FacilityPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class FacilityService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow: AbstractUnitOfWork = uow

    @with_uow
    async def insert(self, facility_post: FacilityPostSchema) -> int:
        """Function  possible make update entity if it is exists"""
        
        external_id = facility_post.external_id

        facility =  await self.uow.facility_repo.find_one(external_id=external_id)
        new_facility = facility_post.model_dump()
        if facility:
            facility_id = await self.uow.facility_repo.edit_one(facility.id, new_facility)
        else:            
            facility_id = await self.uow.facility_repo.add_one(new_facility)
        await self.uow.commit()
        return facility_id

    @with_uow
    async def bulk_insert(self, facilities_post: list[FacilityPostSchema]) -> int:
        """
        Insert facilites
        """
        facilities_data_for_inserting = [facility.model_dump() for facility in facilities_post]
        try:
            await self.uow.facility_repo.bulk_insert(facilities_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Companies between {facilities_post[0].external_id}-{facilities_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, facilities_update: list[FacilityPostSchema]) -> int:
        """
        Insert facilites
        """
        facilities_data_for_updating = [falicity.model_dump() for falicity in facilities_update]
        try:
            await self.uow.facility_repo.bulk_update_by_external_ids(facilities_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Facilites between {facilities_update[0].external_id}-{facilities_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.facility_repo.get_existing_external_ids(ids)
        
    @staticmethod
    async def get_title_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            facilities = await uow.facility_repo.get_all()
            facilities_name_id_mapped: dict[str, int] = {}
            for facility in facilities:
                facilities_name_id_mapped[facility.title] = facility.id
            return facilities_name_id_mapped


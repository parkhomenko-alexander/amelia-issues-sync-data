from loguru import logger
from app.schemas.service_schemas import ServicePostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class ServiceService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, elements_post: list[ServicePostSchema]) -> int:
        """
        Insert services
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.service_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Services between {elements_post[0].external_id}-{elements_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, elements_update: list[ServicePostSchema]) -> int:
        """
        Insert services
        """
        elements_data_for_updating = [workflow.model_dump() for workflow in elements_update]
        try:
            await self.uow.service_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Services between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.service_repo.get_existing_external_ids(ids)

    @staticmethod
    async def get_name_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            services = await uow.service_repo.get_all()
            service_name_id_mapped: dict[str, int] = {}
            for s in services:
                service_name_id_mapped[s.title] = s.id
            return service_name_id_mapped
    
    @staticmethod
    async def get_title_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            res = await uow.service_repo.get_all()
            mapping = {}
            for c in res:
                mapping[c.title] = c.id
            return mapping
        
    @staticmethod
    async def get_mapping_service_id_work_categories(uow: AbstractUnitOfWork) -> dict[int, dict[str, int]]:
        async with uow:
            services_with_categories = await uow.service_repo.get_all_joined_work_categories()
            mapping: dict[int, dict[str, int]] = {}
            for s in services_with_categories:
                mapping_works: dict[str, int] = {}
                if s.work_categories is None: continue 
                for work in s.work_categories:
                    mapping_works[work.title] = work.id
                mapping[s.external_id] = mapping_works

        return mapping
        
    # @with_uow
    # async def get_company(self, id: int) -> CompanyOrmSсheme | None:
    #     res = await self.uow.facility_repo.find_one(external_id = id)

    #     if not res:
    #         return None
    #     return CompanyOrmSсheme.model_validate(res, from_attributes=True)
    
    # @with_uow    
    # async def get_count(self) -> int:
        # res = await self.uow.facility_repo.get_count()
        # return res 
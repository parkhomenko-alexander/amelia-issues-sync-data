from loguru import logger
from app.schemas.company_schemas import CompanyGetSchema, CompanyPostSchema, CompanyOrmSсheme
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class CompanyService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, companies_post: list[CompanyPostSchema]) -> int:
        """
        Insert companies
        """
        companies_data_for_inserting = [company.model_dump() for company in companies_post]
        try:
            await self.uow.company_repo.bulk_insert(companies_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Companies between {companies_post[0].external_id}-{companies_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, companies_update: list[CompanyPostSchema]) -> int:
        """
        Insert companies
        """
        companies_data_for_updating = [company.model_dump() for company in companies_update]
        try:
            await self.uow.company_repo.bulk_update_by_external_ids(companies_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Companies between {companies_update[0].external_id}-{companies_update[-1].external_id} were updated")
        return 0                 

    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.company_repo.get_existing_external_ids(ids)

    # @with_uow
    # async def get_company(self, id: int) -> CompanyOrmSсheme | None:
    #     res = await self.uow.facility_repo.find_one(external_id = id)

    #     if not res:
    #         return None
    #     return CompanyOrmSсheme.model_validate(res, from_attributes=True)
    
    # @with_uow    
    # async def get_count(self) -> int:
    #     res = await self.uow.facility_repo.get_count()
    #     return res
    
    @staticmethod
    async def get_title_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            res = await uow.company_repo.get_all()
            mapping = {}
            for c in res:
                mapping[c.full_name] = c.id
            return mapping

from typing import Sequence
from loguru import logger
from app.schemas.workflow_schemas import WorkflowGetSchema, WorkflowPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class WorkflowService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, workflows_post: list[WorkflowPostSchema]) -> int:
        """
        Insert workflows
        """
        workflows_data_for_inserting = [workflow.model_dump() for workflow in workflows_post]
        try:
            await self.uow.workflow_repo.bulk_insert(workflows_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"workflows between {workflows_post[0].external_id}-{workflows_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, workflows_update: list[WorkflowPostSchema]) -> int:
        """
        Insert workflows
        """
        workflows_data_for_updating = [workflow.model_dump() for workflow in workflows_update]
        try:
            await self.uow.workflow_repo.bulk_update_by_external_ids(workflows_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Companies between {workflows_update[0].external_id}-{workflows_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.workflow_repo.get_existing_external_ids(ids)

    @with_uow
    async def get_all(self) -> list[WorkflowGetSchema]:
        workflows = await self.uow.workflow_repo.get_all()
        
        return [WorkflowGetSchema.model_validate(w, from_attributes=True) for w in workflows]

    @staticmethod
    async def get_external_id_id_mapping(uow: AbstractUnitOfWork) -> dict[int, int]:
        async with uow:
            workflows = await uow.workflow_repo.get_all()

            mapping = {}
            for w in workflows:
                mapping[w.external_id] = w.id
            
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
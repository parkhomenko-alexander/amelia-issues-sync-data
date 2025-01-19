from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.workflow import Workflow
from app.repositories.abstract_repository import SQLAlchemyRepository


class WorkflowRepository(SQLAlchemyRepository[Workflow]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Workflow)
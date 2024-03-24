from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.work_category import WorkCategory
from app.repositories.abstract_repository import SQLAlchemyRepository


class WorkCategoryRepository(SQLAlchemyRepository[WorkCategory]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, WorkCategory)
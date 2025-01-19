from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.priority import Priority
from app.repositories.abstract_repository import SQLAlchemyRepository


class PriorityRepository(SQLAlchemyRepository[Priority]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Priority)
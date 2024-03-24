from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.status import Status
from app.repositories.abstract_repository import SQLAlchemyRepository


class StatusRepository(SQLAlchemyRepository[Status]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Status)
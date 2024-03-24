from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.floor import Floor
from app.repositories.abstract_repository import SQLAlchemyRepository


class FloorRepository(SQLAlchemyRepository[Floor]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Floor)
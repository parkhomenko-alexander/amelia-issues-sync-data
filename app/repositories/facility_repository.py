from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.facility import Facility
from app.repositories.abstract_repository import SQLAlchemyRepository


class FacilityRepository(SQLAlchemyRepository[Facility]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Facility)
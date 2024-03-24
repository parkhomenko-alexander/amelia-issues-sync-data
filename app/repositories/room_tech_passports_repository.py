from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.room_tech_passports import RoomTechPassports
from app.repositories.abstract_repository import SQLAlchemyRepository


class RoomTechPassportsRepository(SQLAlchemyRepository[RoomTechPassports]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, RoomTechPassports)
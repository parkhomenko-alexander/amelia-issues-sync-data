from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.room import Room
from app.repositories.abstract_repository import SQLAlchemyRepository


class RoomRepository(SQLAlchemyRepository[Room]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Room)
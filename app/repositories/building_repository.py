from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models.building import Building 
from app.repositories.abstract_repository import SQLAlchemyRepository


class BuildingRepository(SQLAlchemyRepository[Building]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Building)

    async def get_all_joined_rooms(self) -> Sequence[Building]:
        stmt = (
            select(self.model)
            .options(selectinload(self.model.rooms))
        )

        q_res = await self.async_session.execute(stmt)
        res = q_res.unique().scalars().all()
        return res
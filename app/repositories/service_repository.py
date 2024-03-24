from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.service import Service
from app.repositories.abstract_repository import SQLAlchemyRepository


class ServiceRepository(SQLAlchemyRepository[Service]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Service)

    async def get_all_joined_work_categories(self) -> Sequence[Service]:
        stmt = (
            select(self.model)
            .options(selectinload(self.model.work_categories))
        )

        q_res = await self.async_session.execute(stmt)
        res = q_res.unique().scalars().all()
        return res
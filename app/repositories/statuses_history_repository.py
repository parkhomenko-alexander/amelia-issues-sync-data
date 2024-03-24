from typing import Sequence
from sqlalchemy import Result, Row, Subquery, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.status_history import StatusHistory
from app.repositories.abstract_repository import SQLAlchemyRepository


class StatusHistoryRepository(SQLAlchemyRepository[StatusHistory]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, StatusHistory)

    async def get_last_statuses_for_each_issue(self) -> Sequence[Row[tuple[int, str]]]:
        latest_status_subquery = (
            select(
                    self.model.issue_id,
                    func.max(self.model.external_id).label("latest_id"),
                )
            .group_by(self.model.issue_id)
            .cte("latest_status_subquery")
        )

        latest_status = (
            select(
                self.model.issue_id,
                self.model.status
            ).
            join(
                latest_status_subquery,
                self.model.external_id == latest_status_subquery.c.latest_id
            )
        )

        res = await self.async_session.execute(latest_status)

        return res.all()
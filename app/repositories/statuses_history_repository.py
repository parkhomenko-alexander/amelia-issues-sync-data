from typing import Sequence
from sqlalchemy import CTE, Result, Row, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.abstract_repository import SQLAlchemyRepository

from app.db.models.status_history import StatusHistory
from app.db.models.issue import Issue

class StatusHistoryRepository(SQLAlchemyRepository[StatusHistory]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, StatusHistory)

    async def get_last_statuses_for_each_issue(self, service_id=None) -> Sequence[Row[tuple[int, str]]]:
        latest_status_subquery: CTE = (
            select(
                self.model.issue_id,
                func.max(self.model.external_id).label("latest_id"),
            )
            .group_by(self.model.issue_id)
            .cte("latest_status_subquery")
        )

        latest_status: Select = (
            select(
                self.model.issue_id,
                self.model.status
            )
            .join(
                latest_status_subquery,
                self.model.external_id == latest_status_subquery.c.latest_id
            )
            .join(
                Issue, 
                self.model.issue_id == Issue.external_id
            )
        )

        if service_id is not None:
            latest_status = latest_status.where(Issue.service_id == service_id)

        res: Result = await self.async_session.execute(latest_status)

        return res.all()
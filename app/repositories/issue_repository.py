from typing import Sequence
from sqlalchemy import CTE, Result, Row, Select, Subquery, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.issue import Issue
from app.db.models.status_history import StatusHistory


from app.repositories.abstract_repository import SQLAlchemyRepository



class IssueRepository(SQLAlchemyRepository[Issue]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Issue)

    async def get_all_external_ids_with_excluded_statuses(self, statuses: list[str]) -> Sequence[int]:
        last_statuses_ids: CTE = (
            select(
                StatusHistory.issue_id,
                func.max(StatusHistory.external_id).label("latest_status_id")
            )
            .group_by(StatusHistory.issue_id)
            .cte("latest_status_subquery")
        )

        last_statuses_with_msg: CTE = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status
            )
            .join(
                last_statuses_ids,
                StatusHistory.external_id == last_statuses_ids.c.latest_status_id)
            .cte("latest_statuses_with_message")
        )

        current_issues_with_statuses: Select = (
            select(
                self.model.external_id,
                last_statuses_with_msg.c.status
            )
            .join(
                last_statuses_with_msg,
                self.model.external_id == last_statuses_with_msg.c.issue_id
            )
            .where(last_statuses_with_msg.c.status.not_in(statuses))
        )

        query_res: Result = await self.async_session.execute(current_issues_with_statuses)
        res: Sequence[int] = query_res.scalars().all()

        return res
    
    async def get_all_external_ids_with_included_statuses(self, statuses: list[str]) -> Sequence[int]:
        last_statuses_ids: CTE = (
            select(
                StatusHistory.issue_id,
                func.max(StatusHistory.external_id).label("latest_status_id")
            )
            .group_by(StatusHistory.issue_id)
            .cte("latest_status_subquery")
        )

        last_statuses_with_msg: CTE = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status
            )
            .join(
                last_statuses_ids,
                StatusHistory.external_id == last_statuses_ids.c.latest_status_id)
            .cte("latest_statuses_with_message")
        )

        current_issues_with_statuses: Select = (
            select(
                self.model.external_id,
                last_statuses_with_msg.c.status
            )
            .join(
                last_statuses_with_msg,
                self.model.external_id == last_statuses_with_msg.c.issue_id
            )
            .where(last_statuses_with_msg.c.status.in_(statuses))
        )

        query_res: Result = await self.async_session.execute(current_issues_with_statuses)
        res: Sequence[int] = query_res.scalars().all()

        return res 
from typing import Sequence

from sqlalchemy import CTE, Result, Row, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.issue import Issue
from app.db.models.status_history import StatusHistory
from app.repositories.abstract_repository import SQLAlchemyRepository


class StatusHistoryRepository(SQLAlchemyRepository[StatusHistory]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, StatusHistory)

    async def get_last_statuses_for_each_issue(self, service_id: int | None = None, filter_statuses: list[str] = []) -> Sequence[Row[tuple[int, str]]]:

        latest_status_subquery: CTE = (
            select(
                self.model.issue_id,
                func.max(self.model.external_id).label("latest_id"),
            )
            .group_by(self.model.issue_id)
            .cte("latest_status_subquery")
        )

        filtered_by_service_issues_ids: Select = (
            select(
                Issue.external_id,
                Issue.service_id
            )
        ) 

        if service_id is not None:
            filtered_by_service_issues_ids = filtered_by_service_issues_ids.where(Issue.service_id == service_id)
        
        filtered_by_service_issues_ids_cte: CTE = filtered_by_service_issues_ids.cte("filtered_by_service_issues_ids")

        latest_statuses_stmt = (
            select(
                filtered_by_service_issues_ids_cte.c.external_id,
                self.model.status,
            )
            .outerjoin(
                latest_status_subquery,
                filtered_by_service_issues_ids_cte.c.external_id == latest_status_subquery.c.issue_id
            )
            .outerjoin(
                self.model,
                latest_status_subquery.c.latest_id == self.model.external_id
            )
        )

        if filter_statuses != []:
           latest_statuses_stmt = latest_statuses_stmt.where(
                (self.model.status.is_(None)) |
                (self.model.status.in_(filter_statuses)) 
            )

        res: Result = await self.async_session.execute(latest_statuses_stmt)

        return res.all()
    
    async def get_unique_statuses(self,) -> list[str]:
        stmt: Select = (
            select(
                self.model.status.distinct()
            )
        )

        query_res = await self.async_session.execute(stmt)
        res =  query_res.scalars().all()
        return [r for r in res]
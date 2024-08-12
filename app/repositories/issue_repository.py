from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import CTE, Result, Row, Select, Subquery, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.building import Building
from app.db.models.company import Company
from app.db.models.issue import Issue
from app.db.models.room import Room
from app.db.models.service import Service
from app.db.models.status_history import StatusHistory
from app.db.models.user import User
from app.db.models.work_category import WorkCategory
from app.repositories.abstract_repository import SQLAlchemyRepository


class IssueRepository(SQLAlchemyRepository[Issue]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Issue)

    async def get_all_external_ids_with_included_statuses(self, service_id: int, statuses: list[str]) -> Sequence[int]:
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
                StatusHistory.external_id == last_statuses_ids.c.latest_status_id
            )
            .where(
                StatusHistory.status.in_(statuses)
            )
            .cte("latest_statuses_with_message")
        )

        exsists_issues_in_service: CTE = (
            select(
                self.model.external_id,
            )
            .where(self.model.service_id == service_id)
            .cte("exsists_issues_ext_id")
        )

        current_issues_with_statuses: Select = (
            select(
                exsists_issues_in_service.c.external_id,
                last_statuses_with_msg.c.status
            )
            .outerjoin(
                exsists_issues_in_service,
                exsists_issues_in_service.c.external_id == last_statuses_with_msg.c.issue_id
            )
        )

        query_res: Result = await self.async_session.execute(current_issues_with_statuses)
        res: Sequence[int] = query_res.scalars().all()

        return res
    
    async def get_issues_with_filtered_by_time(self, start_date: datetime, end_date: datetime) -> Sequence[Row]:
        
        filtered_issues_cte: CTE =  (select(
                self.model.description,
                self.model.external_id, 
                self.model.created_at, 
                self.model.finish_date_plane, 
                self.model.dead_line,
                # finished_at
                self.model.rating,
                self.model.tel,
                self.model.email,
                
                self.model.company_id, 
                self.model.service_id,
                self.model.work_category_id,
                self.model.building_id,
                self.model.executor_id, 
                self.model.room_id 
                ).where(
                    and_(
                        self.model.created_at >= start_date,
                        self.model.created_at <= end_date
                    )
                ).order_by(self.model.created_at.desc())
            ).cte("filtered_issues_subquery")
        
        last_statuses_ids_cte: CTE = (
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
                StatusHistory.status,
                StatusHistory.created_at,
            )
            .join(
                last_statuses_ids_cte,
                StatusHistory.external_id == last_statuses_ids_cte.c.latest_status_id
            )
            .cte("latest_statuses_with_message")
        )

        ranked_statuses_cte: CTE = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status,
                StatusHistory.created_at,
                func.row_number().over(
                    partition_by=StatusHistory.issue_id,
                    order_by=StatusHistory.external_id.desc()
                ).label('rank')
            )
            .cte("ranked_statuses_subquery")
        )

        prelast_statuses_cte: CTE = (
            select(
                ranked_statuses_cte.c.issue_id,
                ranked_statuses_cte.c.status,
                ranked_statuses_cte.c.created_at
            )
            .where(ranked_statuses_cte.c.rank == 2)
            .cte("prelast_statuses_with_message")
        )

        stmt: Select = (
            select(filtered_issues_cte, Service.title, WorkCategory.title, Building.title, Room.title, User.first_name, User.middle_name, User.last_name, Company.full_name, last_statuses_with_msg.c.status, last_statuses_with_msg.c.created_at, prelast_statuses_cte.c.status, prelast_statuses_cte.c.created_at)
            .join(Service, Service.external_id == filtered_issues_cte.c.service_id)
            .join(WorkCategory, WorkCategory.id ==  filtered_issues_cte.c.work_category_id)
            .outerjoin(Building, Building.id == filtered_issues_cte.c.building_id)
            .outerjoin(Room, Room.id == filtered_issues_cte.c.room_id)
            .outerjoin(User, User.id == filtered_issues_cte.c.executor_id)
            # .outerjoin(Company, User.id == filtered_issues_cte.c.company_id)
            .outerjoin(Company, User.company_id == Company.id)
            .join(last_statuses_with_msg, last_statuses_with_msg.c.issue_id == filtered_issues_cte.c.external_id)
            .join(prelast_statuses_cte, prelast_statuses_cte.c.issue_id == filtered_issues_cte.c.external_id)
        )
        query_res: Result = await self.async_session.execute(stmt)
        res: Sequence[Row] = query_res.all()

        return res 

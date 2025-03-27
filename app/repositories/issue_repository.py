from datetime import datetime
from functools import lru_cache
from typing import Sequence

from loguru import logger
from sqlalchemy import (ARRAY, CTE, INTEGER, TEXT, Case, ColumnElement, Result, Row,
                        Select, Subquery, TextClause, and_, between, bindparam, desc, func, literal_column, select, text)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Building, Company
from app.db.models import issue
from app.db.models import status_history
from app.db.models.issue import Issue
from app.db.models.priority import Priority
from app.db.models.room import Room
from app.db.models.service import Service
from app.db.models.status_history import StatusHistory
from app.db.models.user import User
from app.db.models.work_category import WorkCategory
from app.dto.issues_filter_dto import IssueFilterDTO
from app.repositories.abstract_repository import SQLAlchemyRepository
from app.utils.benchmark import perfomance_timer


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
        
        filtered_issues_cte: CTE = (select(
                self.model.description,
                self.model.external_id, 
                self.model.created_at, 
                self.model.finish_date_plane, 
                self.model.dead_line,
                # finished_at
                self.model.rating,
                self.model.tel,
                self.model.email,
                self.model.work_place,
                
                self.model.company_id, 
                self.model.service_id,
                self.model.work_category_id,
                self.model.building_id,
                self.model.executor_id, 
                self.model.room_id,
                self.model.priority_id 
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
            # select(filtered_issues_cte, Service.title, WorkCategory.title, Building.title, Room.title, User.first_name, User.middle_name, User.last_name, Company.full_name, last_statuses_with_msg.c.status, last_statuses_with_msg.c.created_at, prelast_statuses_cte.c.status, prelast_statuses_cte.c.created_at, Priority.title)
            select(
                filtered_issues_cte.c.description,  # 0
                filtered_issues_cte.c.external_id,  # 1
                filtered_issues_cte.c.created_at,  # 2
                filtered_issues_cte.c.finish_date_plane,  # 3
                filtered_issues_cte.c.dead_line,  # 4
                filtered_issues_cte.c.rating,  # 5
                filtered_issues_cte.c.tel,  # 6
                filtered_issues_cte.c.email,  # 7
                filtered_issues_cte.c.work_place,  # 8
                Service.title,  # 9
                WorkCategory.title,  # 10
                Building.title,  # 11
                Room.title,  # 12
                User.first_name,  # 13
                User.middle_name,  # 14
                User.last_name,  # 15
                Company.full_name,  # 16
                last_statuses_with_msg.c.status,  # 17
                last_statuses_with_msg.c.created_at,  # 18
                prelast_statuses_cte.c.status,  # 19
                prelast_statuses_cte.c.created_at,  # 20
                Priority.title  # 21
            )
            .join(Service, Service.external_id == filtered_issues_cte.c.service_id)
            .join(WorkCategory, WorkCategory.id ==  filtered_issues_cte.c.work_category_id)
            .outerjoin(Building, Building.id == filtered_issues_cte.c.building_id)
            .outerjoin(Room, Room.id == filtered_issues_cte.c.room_id)
            .outerjoin(User, User.id == filtered_issues_cte.c.executor_id)
            # .outerjoin(Company, User.id == filtered_issues_cte.c.company_id)
            .outerjoin(Company, User.company_id == Company.id)
            .join(last_statuses_with_msg, last_statuses_with_msg.c.issue_id == filtered_issues_cte.c.external_id)
            .join(prelast_statuses_cte, prelast_statuses_cte.c.issue_id == filtered_issues_cte.c.external_id)
            .outerjoin(Priority, Priority.id  == filtered_issues_cte.c.priority_id)
        )
        query_res: Result = await self.async_session.execute(stmt)
        res: Sequence[Row] = query_res.all()

        return res 

    def prepare_conditions(
        self,
        buildings_id: list[int]=[],
        services_id: list[int]=[],
        works_category_id: list[int]=[],
        rooms_id: list[int]=[],
        priorities_id: list[int]=[],
        urgencies: list[str]=[],

    ) -> list[ColumnElement]:
        conditions: list[ColumnElement] = []

        if buildings_id:
            conditions.append(self.model.building_id.in_(buildings_id))
        if services_id:
            conditions.append(self.model.service_id.in_(services_id))
        if works_category_id:
            conditions.append(self.model.work_category_id.in_(works_category_id))
        if rooms_id:
            conditions.append(self.model.room_id.in_(rooms_id))
        if priorities_id:
            conditions.append(self.model.priority_id.in_(priorities_id))
        if urgencies:
            conditions.append(self.model.urgency.in_(urgencies))
        conditions.append(self.model.facility_id==2)
        return conditions

    def build_filtered_issues_sql(
        self,
        select_statement: str = "",
        pagination_statement: str = "",
        order_by_statement: str = ""
    ) -> TextClause:
        stmt = text(
            f"""
            with filtered_by_timings_subq as (
                select 
                    distinct created_in_tr_subq.issue_id
                from (
                    select
                        issue_id
                    from (
                        select
                            issue_id,
                            min(created_at) as min_created_id
                        from statuses_history
                        group by issue_id
                    )
                    where min_created_id  BETWEEN :start_date AND :end_date
                    -- where min_created_id AT TIME ZONE 'Australia/Sydney'  BETWEEN :start_date AND :end_date
                    order by issue_id desc
                ) created_in_tr_subq
                join (
                    select 
                        issue_id
                    from statuses_history
                    where created_at  BETWEEN :transition_start_date AND :transition_end_date
                    -- where created_at AT TIME ZONE 'Australia/Sydney' BETWEEN :transition_start_date AND :transition_end_date
                    and (:transition_statuses IS NULL OR status = ANY(:transition_statuses))  
                ) transmit_in_statuses_subq 
                on created_in_tr_subq.issue_id = transmit_in_statuses_subq.issue_id
            ),

            last_status_filter as (
                select 
                    fbts.issue_id,
                    sh.status,
                    i.building_id,
                    i.service_id,
                    i.work_category_id,
                    i.room_id,
                    i.priority_id,
                    i.urgency,
                    ROW_NUMBER() over (PARTITION BY sh.issue_id order by sh.created_at DESC) as rn
                from statuses_history sh 
                join filtered_by_timings_subq fbts on sh.issue_id = fbts.issue_id
                join issues i ON i.external_id = fbts.issue_id 
            )

            {select_statement}
            from last_status_filter ls_f
            where 
                rn=1 
                AND (:current_statuses IS NULL OR status = ANY(:current_statuses))
                AND (:buildings_id IS NULL OR ls_f.building_id = ANY(:buildings_id))
                AND (:services_id IS NULL OR ls_f.service_id = ANY(:services_id))
                AND (:works_category_id IS NULL OR ls_f.work_category_id = ANY(:works_category_id))
                AND (:rooms_id IS NULL OR ls_f.room_id = ANY(:rooms_id))
                AND (:priorities_id IS NULL OR ls_f.priority_id = ANY(:priorities_id))
                AND (:urgencies IS NULL OR ls_f.urgency = ANY(:urgencies))
            {order_by_statement}
            {pagination_statement}
            """
        ).bindparams(
            bindparam("transition_statuses", type_=ARRAY(TEXT)),
            bindparam("current_statuses", type_=ARRAY(TEXT)),
            bindparam("buildings_id", type_=ARRAY(INTEGER)),
            bindparam("services_id", type_=ARRAY(INTEGER)),
            bindparam("works_category_id", type_=ARRAY(INTEGER)),
            bindparam("rooms_id", type_=ARRAY(INTEGER)),
            bindparam("priorities_id", type_=ARRAY(INTEGER)),
            bindparam("urgencies", type_=ARRAY(TEXT)),
        )

        return stmt

    @perfomance_timer
    async def get_count_issues_with_filters_for_report3(
        self,
        params: IssueFilterDTO
    ) -> int:
        stmt = self.build_filtered_issues_sql("select count(ls_f.issue_id)")
        result = await self.async_session.execute(
            stmt,
            {
                "start_date": params.start_date,
                "end_date": params.end_date,
                "transition_start_date": params.transition_start_date,
                "transition_end_date": params.transition_end_date,
                "transition_statuses": params.transition_statuses,
                "current_statuses": params.current_statuses,
                "buildings_id": params.buildings_id,
                "services_id": params.services_id,
                "works_category_id": params.works_category_id,
                "rooms_id": params.rooms_id,
                "urgencies": None,
                "priorities_id": params.priorities_id,
            }
        )
        r = result.scalar()
        return r or 0

    @perfomance_timer
    async def get_issue_ids_with_filters_for_api_ver3(
        self,
        params: IssueFilterDTO
    ) -> Sequence[int]:
        stmt = self.build_filtered_issues_sql(
            "select ls_f.issue_id",
            "LIMIT :limit OFFSET :offset",
            "ORDER BY ls_f.issue_id DESC",
        )
        result = await self.async_session.execute(
            stmt,
            {
                "start_date": params.start_date,
                "end_date": params.end_date,
                "transition_start_date": params.transition_start_date,
                "transition_end_date": params.transition_end_date,
                "transition_statuses": params.transition_statuses,
                "current_statuses": params.current_statuses,
                "buildings_id": params.buildings_id,
                "services_id": params.services_id,
                "works_category_id": params.works_category_id,
                "rooms_id": params.rooms_id,
                "priorities_id": params.priorities_id,
                "urgencies": None,
                "limit": params.limit,
                "offset": params.limit * params.offset
            }
        )
        r = result.scalars().all()
        return r

    @perfomance_timer
    async def get_issue_ids_with_filters_for_report_ver3(
        self,
        params: IssueFilterDTO
    ) -> Sequence[int]:
        stmt = self.build_filtered_issues_sql(
            "select ls_f.issue_id",
            "ORDER BY ls_f.issue_id DESC"
        )
        result = await self.async_session.execute(
            stmt,
            {
                "start_date": params.start_date,
                "end_date": params.end_date,
                "transition_start_date": params.transition_start_date,
                "transition_end_date": params.transition_end_date,
                "transition_statuses": params.transition_statuses,
                "current_statuses": params.current_statuses,
                "buildings_id": params.buildings_id,
                "services_id": params.services_id,
                "works_category_id": params.works_category_id,
                "rooms_id": params.rooms_id,
                "priorities_id": params.priorities_id,
                "urgencies": None,
            }
        )
        r = result.scalars().all()
        return r

    @perfomance_timer
    async def get_filtered_issues_for_report_ver4(self, chunk: Sequence[int]) -> Sequence[Row]:
        chunk_ids_cte = (
            select(
                func.unnest(literal_column(f"ARRAY{chunk}::INTEGER[]")).label("chunk_ids")
            ).cte("ChunkIDs")
        )
        
        # Compute ranked statuses once
        ranked_statuses_cte = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status,
                func.timezone("UTC-10", StatusHistory.created_at).label("rank_created_at"),
                func.row_number()
                .over(partition_by=StatusHistory.issue_id, order_by=desc(StatusHistory.external_id))
                .label("rank"),
            )
            # .where(StatusHistory.issue_id.in_(chunk))
            .join(chunk_ids_cte, StatusHistory.issue_id == chunk_ids_cte.c.chunk_ids)  # Faster than WHERE IN
            .cte("RankedStatuses")
        )
        # query_res: Result = await self.async_session.execute(select(ranked_statuses_cte))
        # r1:  Sequence[Row] = query_res.all()

        ranked_issues_cte = (
            select(
                ranked_statuses_cte.c.issue_id,
                func.max(ranked_statuses_cte.c.rank).label("max_rank"),

                func.max(
                    Case(
                        (ranked_statuses_cte.c.rank == 1, ranked_statuses_cte.c.status),
                        else_=None
                    )
                ).label("last_status"),

                func.max(
                    Case(
                        (ranked_statuses_cte.c.rank == 1, ranked_statuses_cte.c.rank_created_at),
                        else_=None
                    )
                ).label("last_status_created"),

                func.max(
                    Case(
                        (ranked_statuses_cte.c.rank == 2, ranked_statuses_cte.c.status),
                        else_=None
                    )
                ).label("pred_status"),

                func.max(
                    Case(
                        (ranked_statuses_cte.c.rank == 2, ranked_statuses_cte.c.rank_created_at),
                        else_=None
                    )
                ).label("pred_status_created"),

                func.min(
                    ranked_statuses_cte.c.rank_created_at
                ).label("first_status_created"),
            )
            .group_by(ranked_statuses_cte.c.issue_id)
            .cte("RankedIssues")
        )
        # query_res: Result = await self.async_session.execute(select(ranked_issues_cte))
        # r2:  Sequence[Row] = query_res.all()
        # Final query joining issues with computed ranked statuses
        base_query = (
            select(
                self.model.external_id,
                self.model.description.label("iss_descr"),
                self.model.rating,
                self.model.urgency,
                self.model.work_place,
                func.timezone("UTC-10", self.model.finish_date_plane).label("finish_date_plane"),
                Service.title.label("service_title"),
                WorkCategory.title.label("wc_title"),
                Building.title.label("building_title"),
                Room.title.label("room_title"),
                Priority.title.label("prior_title"),

                ranked_issues_cte.c.last_status,
                ranked_issues_cte.c.last_status_created,
                ranked_issues_cte.c.pred_status,
                ranked_issues_cte.c.pred_status_created,
                ranked_issues_cte.c.first_status_created,
            )
            .join_from(ranked_issues_cte, self.model, self.model.external_id == ranked_issues_cte.c.issue_id)
            .join(Service, self.model.service_id == Service.external_id)
            .join(WorkCategory, self.model.work_category_id == WorkCategory.id)
            .join(Building, self.model.building_id == Building.id)
            .outerjoin(Room, self.model.room_id == Room.id)
            .outerjoin(Priority, self.model.priority_id == Priority.id)
            .order_by(self.model.external_id.desc())
        )

        query_res: Result = await self.async_session.execute(base_query)
        res: Sequence[Row] = query_res.all()
        return res

    async def get_last_statuses_by_id(self, issues_ids: list[int]) -> Sequence[Row[tuple[int, str]]]:
        max_statuses_ids_cte: CTE = (
            select(
                StatusHistory.issue_id,
                func.max(StatusHistory.external_id).label("latest_status_id")
            ).
            where(StatusHistory.issue_id.in_(issues_ids)).
            group_by(StatusHistory.issue_id).
            cte("latest_status_cte")
        )

        last_statuses_with_msg: CTE = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status
            )
            .join(
                max_statuses_ids_cte, StatusHistory.external_id == max_statuses_ids_cte.c.latest_status_id
            )
            .cte("latest_statuses_with_message")
        )

        stmt = (
            select(last_statuses_with_msg.c.issue_id, last_statuses_with_msg.c.status)
        )

        query_res = await self.async_session.execute(stmt)
        res = query_res.all()
        return res
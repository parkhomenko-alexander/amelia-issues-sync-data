from datetime import datetime
from functools import lru_cache
from typing import Sequence

from loguru import logger
from sqlalchemy import (CTE, Case, ColumnElement, Result, Row,
                        Select, Subquery, and_, between, desc, func, literal_column, select)
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


    # async def get_issues_with_filters_for_report_ver2(
    async def get_issue_ids_with_filters_for_report_ver2(
        self,
        start_date: datetime,
        end_date: datetime,
        transition_start_date: datetime,
        transition_end_date: datetime,
        transition_statuses: list[str]=[],
        buildings_id: list[int]=[],
        services_id: list[int]=[],
        works_category_id: list[int]=[],
        rooms_id: list[int]=[],
        priorities_id: list[int]=[],
        urgencies: list[str]=[],
        limit: int=0,
        page: int=0,
        current_statuses: list[str] = []
    ) -> Sequence[int]:
        
        conditions: list[ColumnElement] = self.prepare_conditions(buildings_id, services_id, works_category_id, rooms_id, priorities_id,
            urgencies
        )

        # ! перешедшие в статусы по дате
        transition_in_statuses_by_period: Subquery = (
            select(
                StatusHistory.issue_id.distinct().label("issue_id")
            )
            .where(
                and_(
                    StatusHistory.created_at.between(transition_start_date, transition_end_date),
                    StatusHistory.status.in_(transition_statuses)
                )
            )
            .subquery()
        )

        
        query_res: Result = await self.async_session.execute(select(transition_in_statuses_by_period))
        res2: Sequence[Row] = query_res.all()

        # ! отфильтрованные по фильтрам
        filter_trinsition_issues_cte: Subquery = (
            select(
                transition_in_statuses_by_period.c.issue_id
            )
            .join(
                self.model, transition_in_statuses_by_period.c.issue_id == self.model.external_id
            )
            .where(
                and_(
                    *conditions,
                )
            )
            .subquery()
        )

        # query_res: Result = await self.async_session.execute(select(filter_trinsition_issues_cte))
        # res3: Sequence[Row] = query_res.all()

        #! отфильтрованные по дате создания
        issues_created_cte: CTE = (
            select(
                StatusHistory.issue_id,
                func.min(StatusHistory.external_id).label("min_external_status_id"),
                func.timezone("UTC-10", func.min(StatusHistory.created_at)).label("min_created_at")
            )
            .group_by(StatusHistory.issue_id)
            .cte()
        )

        # query_res: Result = await self.async_session.execute(select(issues_created_cte))
        # res4: Sequence[Row] = query_res.all()

        issues_created_filtered_by_time_range_cte = (
            select(
                issues_created_cte.c.issue_id,
            )
            .where(
                between(
                    issues_created_cte.c.min_created_at,
                    start_date,
                    end_date
                )
            )
            .alias("issues_created_filtered_by_time_range_cte")
        )
        # query_res: Result = await self.async_session.execute(select(issues_created_filtered_by_time_range_cte))
        # res5: Sequence[Row] = query_res.all()

        last_status_id_for_filtered_issues = (
            select(
                issues_created_filtered_by_time_range_cte.c.issue_id,
                func.max(StatusHistory.external_id).label("latest_status_id")
            )
            .join(issues_created_filtered_by_time_range_cte, StatusHistory.issue_id == issues_created_filtered_by_time_range_cte.c.issue_id)
            .group_by(issues_created_filtered_by_time_range_cte.c.issue_id)
            .alias("last_status_id_for_filtered_issues")
        )

        # query_res: Result = await self.async_session.execute(select(last_status_id_for_filtered_issues))
        # res5: Sequence[Row] = query_res.all()


        filtered_issues_id_by_current_statuses = (
            select(
                last_status_id_for_filtered_issues.c.issue_id,
                StatusHistory.status
            )
            .join(StatusHistory, last_status_id_for_filtered_issues.c.latest_status_id == StatusHistory.external_id)
        )

        if current_statuses != []:
            filtered_issues_id_by_current_statuses = filtered_issues_id_by_current_statuses.where(
                StatusHistory.status.in_(current_statuses)
            )
        filtered_issues_id_by_current_statuses = filtered_issues_id_by_current_statuses.alias("filtered_issues_id_by_current_statuses")

        # query_res: Result = await self.async_session.execute(select(filtered_issues_id_by_current_statuses))
        # res7: Sequence[Row] = query_res.all()


        # ! итоговые id с которыми будет работа
        join_transition_with_cretion_at_time_cte: Select = (
            select(
                filter_trinsition_issues_cte.c.issue_id,
            )
            .join(filtered_issues_id_by_current_statuses, filter_trinsition_issues_cte.c.issue_id == filtered_issues_id_by_current_statuses.c.issue_id)
            .order_by(filter_trinsition_issues_cte.c.issue_id.desc())
            .limit(limit)
            .offset(limit*page)
        )

        query_res: Result = await self.async_session.execute(join_transition_with_cretion_at_time_cte)
        res6:  Sequence[int] = query_res.scalars().all()
        return res6 

    async def get_filtered_issues_for_report_ver2(self, chunk: list[int]):
        ranked_statuses_for_joined_issues_cte: Subquery = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status,
                StatusHistory.created_at,
                func.row_number().over(
                    partition_by=StatusHistory.issue_id, order_by=desc(StatusHistory.external_id)
                ).label("rank")
            )
            .where(
                StatusHistory.issue_id.in_(
                chunk
            ))
            .subquery()
        )
        # query_res: Result = await self.async_session.execute(select(ranked_statuses_for_joined_issues_cte))
        # res7:  Sequence[Row] = query_res.all()

        last_status_cte: Subquery = (
            select(
                ranked_statuses_for_joined_issues_cte.c.issue_id,
                ranked_statuses_for_joined_issues_cte.c.status.label("last_status"),
                func.timezone("UTC-10", ranked_statuses_for_joined_issues_cte.c.created_at).label("last_status_created"),
            )
            .where(ranked_statuses_for_joined_issues_cte.c.rank == 1)
            .subquery()
        )
        # query_res: Result = await self.async_session.execute(select(last_status_cte))
        # res8:  Sequence[Row] = query_res.all()

        pred_last_status_cte: Subquery = (
            select(
                ranked_statuses_for_joined_issues_cte.c.issue_id,
                ranked_statuses_for_joined_issues_cte.c.status.label("pred_status"),
                func.timezone("UTC-10", ranked_statuses_for_joined_issues_cte.c.created_at).label("pred_status_created"),
                last_status_cte.c.last_status,
                last_status_cte.c.last_status_created
            )
            .join(last_status_cte, and_(
                    last_status_cte.c.issue_id==ranked_statuses_for_joined_issues_cte.c.issue_id,
                    ranked_statuses_for_joined_issues_cte.c.rank==2
                )
            )
            .subquery()
        )
        # query_res: Result = await self.async_session.execute(select(pred_last_status_cte))
        # res9:  Sequence[Row] = query_res.all()

        first_status_by_rank_cte: Subquery = (
            select(
                ranked_statuses_for_joined_issues_cte.c.issue_id,
                func.max(ranked_statuses_for_joined_issues_cte.c.rank).label("first_stat_rank")
            )
            .group_by(ranked_statuses_for_joined_issues_cte.c.issue_id)
            .subquery()
        )
        # query_res: Result = await self.async_session.execute(select(first_status_by_rank_cte))
        # res10:  Sequence[Row] = query_res.all()
        
        first_status_cte: Subquery = (
            select(
                first_status_by_rank_cte.c.issue_id,
                ranked_statuses_for_joined_issues_cte.c.status,
                func.timezone("UTC-10", ranked_statuses_for_joined_issues_cte.c.created_at).label("first_status_created"),
            )
            .join(first_status_by_rank_cte, and_(
                    first_status_by_rank_cte.c.issue_id == ranked_statuses_for_joined_issues_cte.c.issue_id,
                    first_status_by_rank_cte.c.first_stat_rank == ranked_statuses_for_joined_issues_cte.c.rank,
                )
            )
            .subquery()
        )
        # query_res: Result = await self.async_session.execute(select(first_status_cte))
        # res11:  Sequence[Row] = query_res.all()

        joined_times_subquery = (
            select(
                pred_last_status_cte.c.issue_id,
                pred_last_status_cte.c.last_status,
                pred_last_status_cte.c.last_status_created,

                first_status_cte.c.first_status_created,

                pred_last_status_cte.c.pred_status,
                pred_last_status_cte.c.pred_status_created,
            )
            .join(first_status_cte, pred_last_status_cte.c.issue_id == first_status_cte.c.issue_id)
            .subquery()
        )

        # query_res: Result = await self.async_session.execute(select(joined_times_subquery))
        # res13:  Sequence[Row] = query_res.all()

        joined_issues: Select = (
            select(
                self.model.external_id,
                self.model.description.label("iss_descr"),
                self.model.rating,
                self.model.urgency,
                self.model.work_place,
                func.timezone("UTC-10", self.model.finish_date_plane).label("finish_date_plane"),

                Service.title.label("service_title"),
                WorkCategory.title.label("wc_title"),

                joined_times_subquery.c.last_status,
                joined_times_subquery.c.last_status_created,

                joined_times_subquery.c.first_status_created,

                joined_times_subquery.c.pred_status,
                joined_times_subquery.c.pred_status_created,


                Building.title.label("building_title"),

                Room.title.label("room_title"),

                Priority.title.label("prior_title"),
            )
            .join(joined_times_subquery, self.model.external_id == joined_times_subquery.c.issue_id)
            .join(Service, self.model.service_id == Service.external_id)
            .join(WorkCategory, self.model.work_category_id == WorkCategory.id)
            .join(Building, self.model.building_id == Building.id)
            .outerjoin(Room, self.model.room_id == Room.id)
            .outerjoin(Priority, self.model.priority_id == Priority.id)
        )
        query_res: Result = await self.async_session.execute(joined_issues)
        res:  Sequence[Row] = query_res.all()

        return res 



    async def get_filtered_issues_for_report_ver3(self, chunk: list[int]):

        ranked_statuses_subq = (
            select(
                StatusHistory.issue_id,
                StatusHistory.status,
                func.timezone("UTC-10", StatusHistory.created_at).label("rank_created_at"),
                func.row_number()
                .over(partition_by=StatusHistory.issue_id, order_by=desc(StatusHistory.external_id))
                .label("rank")
            )
            .where(StatusHistory.issue_id.in_(chunk))
            .subquery("RankedStatuses")
        )
        # query_res: Result = await self.async_session.execute(select(ranked_statuses_subq))
        # r1:  Sequence[Row] = query_res.all()

        max_rank_statuses_subq = (
            select(
                ranked_statuses_subq.c.issue_id,
                func.max(ranked_statuses_subq.c.rank).label("max_rank")
            )
            .group_by(ranked_statuses_subq.c.issue_id)
            .subquery("MaxRankForFirstStatus")
        )

        first_stasuses_subq = (
            select(
                ranked_statuses_subq.c.issue_id,
                # ranked_statuses_subq.c.status.label("first_status"),
                ranked_statuses_subq.c.rank_created_at.label("first_status_created")
            )
            .join_from(
                max_rank_statuses_subq,
                ranked_statuses_subq,
                onclause=and_(
                    max_rank_statuses_subq.c.issue_id==ranked_statuses_subq.c.issue_id,
                    max_rank_statuses_subq.c.max_rank==ranked_statuses_subq.c.rank
                )
            )
            .subquery("FirstStatuses")
        )
        # query_res: Result = await self.async_session.execute(select(first_stasuses_subq))
        # r2:  Sequence[Row] = query_res.all()

        last_status_subq = (
             select(
                ranked_statuses_subq.c.issue_id,
                ranked_statuses_subq.c.status.label("last_status"),
                ranked_statuses_subq.c.rank_created_at.label("last_status_created")
            )
            .where(ranked_statuses_subq.c.rank==1)
            .subquery("LastStatus")
        )
        # query_res: Result = await self.async_session.execute(select(last_status_subq))
        # r3:  Sequence[Row] = query_res.all()

        pred_last_status_subq = (
             select(
                ranked_statuses_subq.c.issue_id,
                ranked_statuses_subq.c.status.label("pred_status"),
                ranked_statuses_subq.c.rank_created_at.label("pred_status_created")
            )
            .where(ranked_statuses_subq.c.rank==2)
            .subquery("PrevLastStatus")
        )
        # query_res: Result = await self.async_session.execute(select(pred_last_status_subq))
        # r4:  Sequence[Row] = query_res.all()


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

                last_status_subq.c.last_status,
                last_status_subq.c.last_status_created,

                pred_last_status_subq.c.pred_status,
                pred_last_status_subq.c.pred_status_created,

                first_stasuses_subq.c.first_status_created
            )
            .join_from(
                first_stasuses_subq,
                self.model,
                first_stasuses_subq.c.issue_id==self.model.external_id,
            )
            .join_from(
                first_stasuses_subq,
                last_status_subq,
                first_stasuses_subq.c.issue_id==last_status_subq.c.issue_id,
                isouter=True
            )
            .join_from(
                first_stasuses_subq,
                pred_last_status_subq,
                first_stasuses_subq.c.issue_id==pred_last_status_subq.c.issue_id,
                isouter=True
            )
            .join(Service, self.model.service_id == Service.external_id)
            .join(WorkCategory, self.model.work_category_id == WorkCategory.id)
            .join(Building, self.model.building_id == Building.id)
            .outerjoin(Room, self.model.room_id == Room.id)
            .outerjoin(Priority, self.model.priority_id == Priority.id)
        )

        query_res: Result = await self.async_session.execute(base_query)
        res: Sequence[Row] = query_res.all()
        return res


    async def get_filtered_issues_for_report_ver4(self, chunk: list[int]) :
        t1 = datetime.now()
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

        # Select first, last, and previous statuses from ranked table
        ranked_issues_cte = (
            select(
                ranked_statuses_cte.c.issue_id,
                func.max(ranked_statuses_cte.c.rank).label("max_rank"),  # Find max rank per issue

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
                    ranked_statuses_cte.c.rank_created_at  # Get the earliest status created time
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
        )

        query_res: Result = await self.async_session.execute(base_query)
        res: Sequence[Row] = query_res.all()
        t2 = datetime.now()
        logger.info((t2-t1).total_seconds())
        return res

    # @lru_cache(maxsize=30)
    async def get_count_issues_with_filters_for_report_ver2(
    self,
    start_date: datetime,
    end_date: datetime,
    transition_start_date: datetime,
    transition_end_date: datetime,
    transition_statuses: list[str]=[],
    buildings_id: list[int]=[],
    services_id: list[int]=[],
    works_category_id: list[int]=[],
    rooms_id: list[int]=[],
    priorities_id: list[int]=[],
    urgencies: list[str]=[],
    current_statuses: list[str]=[],
) -> int | None:
        conditions: list[ColumnElement] = self.prepare_conditions(buildings_id, services_id, works_category_id, rooms_id, priorities_id,
            urgencies
        )

        # ! перешедшие в статусы по дате
        transition_in_statuses_by_period: Subquery = (
            select(
                StatusHistory.issue_id.distinct().label("issue_id")
            )
            .where(
                and_(
                    StatusHistory.created_at.between(transition_start_date, transition_end_date),
                    StatusHistory.status.in_(transition_statuses)
                )
            )
            .subquery()
        )


        # query_res: Result = await self.async_session.execute(select(transition_in_statuses_by_period))
        # res2: Sequence[Row] = query_res.all()

        # ! отфильтрованные по фильтрам
        filter_trinsition_issues_cte: CTE = (
            select(
                transition_in_statuses_by_period.c.issue_id
            )
            .join(
                self.model, transition_in_statuses_by_period.c.issue_id == self.model.external_id
            )
            .where(
                and_(
                    *conditions,
                )
            )
            .cte()
        )

        # query_res: Result = await self.async_session.execute(select(filter_trinsition_issues_cte))
        # res3: Sequence[Row] = query_res.all()

        #! отфильтрованные по дате создания
        issues_created_cte: CTE = (
            select(
                StatusHistory.issue_id,
                func.min(StatusHistory.external_id).label("min_external_status_id"),
                func.timezone("UTC-10", func.min(StatusHistory.created_at)).label("min_created_at")
            )
            .group_by(StatusHistory.issue_id)
            .cte()
        )

        # query_res: Result = await self.async_session.execute(select(issues_created_cte))
        # res4: Sequence[Row] = query_res.all()

        issues_created_filtered_by_time_range_cte = (
            select(
                issues_created_cte.c.issue_id,
            )
            .where(
                between(
                    issues_created_cte.c.min_created_at,
                    start_date,
                    end_date
                )
            )
            .alias("issues_created_filtered_by_time_range_cte")
        )
        # query_res: Result = await self.async_session.execute(select(issues_created_filtered_by_time_range_cte))
        # res5: Sequence[Row] = query_res.all()

        last_status_id_for_filtered_issues = (
            select(
                issues_created_filtered_by_time_range_cte.c.issue_id,
                func.max(StatusHistory.external_id).label("latest_status_id")
            )
            .join(issues_created_filtered_by_time_range_cte, StatusHistory.issue_id == issues_created_filtered_by_time_range_cte.c.issue_id)
            .group_by(issues_created_filtered_by_time_range_cte.c.issue_id)
            .alias("last_status_id_for_filtered_issues")
        )

        # query_res: Result = await self.async_session.execute(select(last_status_id_for_filtered_issues))
        # res5: Sequence[Row] = query_res.all()


        filtered_issues_id_by_current_statuses = (
            select(
                last_status_id_for_filtered_issues.c.issue_id,
                StatusHistory.status
            )
            .join(StatusHistory, last_status_id_for_filtered_issues.c.latest_status_id == StatusHistory.external_id)
        )

        if current_statuses != []:
            filtered_issues_id_by_current_statuses = filtered_issues_id_by_current_statuses.where(
                StatusHistory.status.in_(current_statuses)
            )
        filtered_issues_id_by_current_statuses = filtered_issues_id_by_current_statuses.alias("filtered_issues_id_by_current_statuses")

        # query_res: Result = await self.async_session.execute(select(filtered_issues_id_by_current_statuses))
        # res7: Sequence[Row] = query_res.all()


        # ! итоговые id с которыми будет работа
        join_transition_with_cretion_at_time_cte = (
            select(
                func.count(filter_trinsition_issues_cte.c.issue_id),
            )
            .join(filtered_issues_id_by_current_statuses, filter_trinsition_issues_cte.c.issue_id == filtered_issues_id_by_current_statuses.c.issue_id)
        )

        query_res: Result = await self.async_session.execute(join_transition_with_cretion_at_time_cte)
        res6 = query_res.scalar()

        return res6


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
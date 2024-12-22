from datetime import datetime
from typing import Sequence

from sqlalchemy import (CTE, BinaryExpression, Result, Row, Select, and_,
                        between, desc, func, select)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Building, Company
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

    ) -> list[BinaryExpression]:
        conditions: list[BinaryExpression] = []

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

        return conditions

    
    async def get_issues_with_filters_for_report_ver2(
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
        limit: int = 50, 
        page: int = 0
    ) -> Sequence[Row]:
        
        conditions: list[BinaryExpression] = self.prepare_conditions(buildings_id, services_id, works_category_id, rooms_id, priorities_id,
            urgencies
        )

        # ! перешедшие в статусы по дате
        transition_in_statuses_by_period: CTE = (
            select(
                StatusHistory.issue_id.distinct().label("issue_id")
            )
            .where(
                and_(
                    StatusHistory.created_at.between(transition_start_date, transition_end_date),
                    StatusHistory.status.in_(transition_statuses)
                )
            )
            .cte()
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

        issues_created_filtered_by_time_range_cte: CTE = (
            select(
                issues_created_cte.c.issue_id,
                issues_created_cte.c.min_external_status_id,
                issues_created_cte.c.min_created_at
            )
            .where(
                between(
                    issues_created_cte.c.min_created_at,
                    start_date,
                    end_date
                )
            )
            .order_by(issues_created_cte.c.issue_id)
            .cte()
        )
        # query_res: Result = await self.async_session.execute(select(issues_created_filtered_by_time_range_cte))
        # res5: Sequence[Row] = query_res.all()

        # ! итоговые id с которыми будет работа
        join_transition_with_cretion_at_time_cte: CTE = (
            select(
                filter_trinsition_issues_cte.c.issue_id,
            )
            .join(issues_created_filtered_by_time_range_cte, filter_trinsition_issues_cte.c.issue_id == issues_created_filtered_by_time_range_cte.c.issue_id)
            .limit(limit)
            .offset(limit*page)
            .cte()
        )

        # query_res: Result = await self.async_session.execute(select(join_transition_with_cretion_at_time_cte))
        # res6:  Sequence[Row] = query_res.all()

        ranked_statuses_for_joined_issues_cte: CTE =(
            select(
                join_transition_with_cretion_at_time_cte.c.issue_id,
                StatusHistory.status,
                StatusHistory.created_at,
                func.row_number().over(
                    partition_by=StatusHistory.issue_id, order_by=desc(StatusHistory.external_id)
                ).label("rank")
            )
            .join(StatusHistory, join_transition_with_cretion_at_time_cte.c.issue_id == StatusHistory.issue_id)
            .cte()
        )
        # query_res: Result = await self.async_session.execute(select(ranked_statuses_for_joined_issues_cte))
        # res7:  Sequence[Row] = query_res.all()

        last_status_cte: CTE = (
            select(
                ranked_statuses_for_joined_issues_cte.c.issue_id,
                ranked_statuses_for_joined_issues_cte.c.status,
                func.timezone("UTC-10", ranked_statuses_for_joined_issues_cte.c.created_at).label("last_status_created"),
            )
            .where(ranked_statuses_for_joined_issues_cte.c.rank == 1)
            .cte()
        )
        # query_res: Result = await self.async_session.execute(select(last_status_cte))
        # res8:  Sequence[Row] = query_res.all()

        pred_last_status_cte: CTE = (
            select(
                ranked_statuses_for_joined_issues_cte.c.issue_id,
                ranked_statuses_for_joined_issues_cte.c.status,
                func.timezone("UTC-10", ranked_statuses_for_joined_issues_cte.c.created_at).label("pred_status_created"),
            )
            .where(ranked_statuses_for_joined_issues_cte.c.rank == 2)
            .cte()
        )
        # query_res: Result = await self.async_session.execute(select(pred_last_status_cte))
        # res9:  Sequence[Row] = query_res.all()

        first_status_by_rank_cte: CTE = (
            select(
                ranked_statuses_for_joined_issues_cte.c.issue_id,
                func.max(ranked_statuses_for_joined_issues_cte.c.rank).label("first_stat_rank")
            )
            .group_by(ranked_statuses_for_joined_issues_cte.c.issue_id)
            .cte()
        )
        # query_res: Result = await self.async_session.execute(select(first_status_by_rank_cte))
        # res10:  Sequence[Row] = query_res.all()
        
        first_status_cte: CTE = (
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
            .cte()
        )
        # query_res: Result = await self.async_session.execute(select(first_status_cte))
        # res11:  Sequence[Row] = query_res.all()

        joined_issues: Select = (
            select(
                join_transition_with_cretion_at_time_cte.c.issue_id,
                self.model.description.label("iss_descr"),
                self.model.rating,
                self.model.urgency,
                self.model.work_place,
                func.timezone("UTC-10", self.model.finish_date_plane).label("finish_date_plane"),
                Service.title.label("service_title"),
                WorkCategory.title.label("wc_title"),
                last_status_cte.c.status.label("last_status"),

                first_status_cte.c.first_status_created.label("created_at_first_stat"),
                last_status_cte.c.last_status_created.label("created_at_last_stat"),
                pred_last_status_cte.c.status.label("predlast_status"),
                pred_last_status_cte.c.pred_status_created.label("created_at_predlast_stat"),


                Building.title.label("building_title"),
                Room.title.label("room_title"),
                Priority.title.label("prior_title"),
                
            )
            .join(self.model, join_transition_with_cretion_at_time_cte.c.issue_id == self.model.external_id)
            .join(Service, self.model.service_id == Service.external_id)
            .join(WorkCategory, self.model.work_category_id == WorkCategory.id)
            .join(last_status_cte, self.model.external_id == last_status_cte.c.issue_id)
            .join(first_status_cte, self.model.external_id == first_status_cte.c.issue_id)
            .join(pred_last_status_cte, self.model.external_id == pred_last_status_cte.c.issue_id)
            .join(Building, self.model.building_id == Building.id)
            .outerjoin(Room, self.model.room_id == Room.id)
            .join(Priority,self.model.priority_id == Priority.id)
        )
        query_res: Result = await self.async_session.execute(joined_issues)
        res:  Sequence[Row] = query_res.all()

        return res 


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
    limit: int = 50, 
    page: int = 0
) -> int | None:
    
        conditions: list[BinaryExpression] = self.prepare_conditions(buildings_id, services_id, works_category_id, rooms_id, priorities_id,
            urgencies
        )

        # ! перешедшие в статусы по дате
        transition_in_statuses_by_period: CTE = (
            select(
                StatusHistory.issue_id.distinct().label("issue_id")
            )
            .where(
                and_(
                    StatusHistory.created_at.between(transition_start_date, transition_end_date),
                    StatusHistory.status.in_(transition_statuses)
                )
            )
            .cte()
        )

        
        query_res: Result = await self.async_session.execute(select(transition_in_statuses_by_period))
        res2: Sequence[Row] = query_res.all()

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

        query_res: Result = await self.async_session.execute(select(filter_trinsition_issues_cte))
        res3: Sequence[Row] = query_res.all()

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

        query_res: Result = await self.async_session.execute(select(issues_created_cte))
        res4: Sequence[Row] = query_res.all()

        issues_created_filtered_by_time_range_cte: CTE = (
            select(
                issues_created_cte.c.issue_id,
                issues_created_cte.c.min_external_status_id,
                issues_created_cte.c.min_created_at
            )
            .where(
                between(
                    issues_created_cte.c.min_created_at,
                    start_date,
                    end_date
                )
            )
            .order_by(issues_created_cte.c.issue_id)
            .cte()
        )
        query_res: Result = await self.async_session.execute(select(issues_created_filtered_by_time_range_cte))
        res5: Sequence[Row] = query_res.all()

        # ! итоговые id с которыми будет работа
        join_transition_with_cretion_at_time_cte: CTE = (
            select(
                func.count(filter_trinsition_issues_cte.c.issue_id),
            )
            .join(issues_created_filtered_by_time_range_cte, filter_trinsition_issues_cte.c.issue_id == issues_created_filtered_by_time_range_cte.c.issue_id)
            .cte()
        )

        query_res: Result = await self.async_session.execute(select(join_transition_with_cretion_at_time_cte))
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
    

from functools import lru_cache
import os
import traceback
from datetime import datetime, timedelta
from typing import Sequence

from loguru import logger
from numpy import sort
from openpyxl import Workbook
from sqlalchemy import Row
from yaml import TagToken

from app.celery.helpers import ShortIssue
from app.db.models import work_category
from app.dto.issues_filter_dto import IssueFilterDTO
from app.dto.mappers.issue_filters_mapper import map_filters_to_dto
from app.schemas.issue_schemas import (FilteredIssue, FilteredIssuesGetSchema,
                                       IssueFilters, IssuePostSchema,
                                       IssuesFiltersSchema, ThinDict, WorkCat)
from app.schemas.status_schemas import HistoryStatusRecord
from app.services.services_helper import with_uow
from app.utils.benchmark import perfomance_timer
from app.utils.redis_manager import CachePrefixes, RedisManager
from app.utils.unit_of_work import AbstractUnitOfWork

from time import time

class IssueService():
    def __init__(self,
                 uow: AbstractUnitOfWork,
                 redis: RedisManager = RedisManager()):
        self.uow = uow
        self.redis = redis

    @with_uow
    async def bulk_insert(self, elements_post: list[IssuePostSchema]) -> int:
        """
        Issues inserting
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.issues_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Issues between {elements_post[0].external_id}-{elements_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, elements_update: list[IssuePostSchema]) -> int:
        """
        Issues updating
        """
        elements_data_for_updating = [e.model_dump() for e in elements_update]
        try:
            await self.uow.issues_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Issues between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.issues_repo.get_existing_external_ids(ids)
    
    @with_uow
    async def bulk_delete(self, elements_id: list[int]) -> int: 
        """
        Bulk delete issues
        """
        try:
            await self.uow.issues_repo.bulk_delete(elements_id)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Issues {elements_id[0]}, ... was remove")
        return 0

    @with_uow
    async def generate_issues_report(self, start_date: datetime, end_date:datetime, hours_delta: int = 0 ) -> str | None:
        """
        Generate issues report
        """
        try:
            result: Sequence[Row] = await self.uow.issues_repo.get_issues_with_filtered_by_time(start_date, end_date)
            workbook = Workbook()
            sheet = workbook.active

            header_order = [
                "id", "service_title", "work_category_title", "state", "description",
                "created_at","finished_at","dead_line","executed_at", "rating", "building_full_title","room_title",
                "Тип помещения","executor_full_name","company","parsed_room_title", "finish_date_plane",
                "Приоритет", "Место проведения"
            ]
            
            if sheet != None:
                sheet.append(header_order)

                for row in result:
                    room_title_row = row[12]
                    if room_title_row is not None and " " in room_title_row:
                        room_title, room_type = row[12].split(" ", 1)
                    else:
                        room_title = room_title_row if room_title_row is not None else "Уточнить" 
                        room_type = ""
                    work_place = row[8]

                    pre_last_status = row[19]
                    last_status = row[17]

                    if row[4] is None:
                        dead_line = ""
                    else:
                        dead_line = (row[4] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S')

                    if last_status in ["исполнена", "отказано"] :
                        executed = (row[18] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S') 
                        finished = ""
                    elif pre_last_status == "исполнена" and last_status == "закрыта":
                        executed = (row[20] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S') 
                        finished = (row[18] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S')
                    else:
                        executed = ""
                        finished = ""
                    
                    finished_at = row[3]
                    if finished_at is None:
                        finished_at = ""
                    else:
                        finished_at = (row[3] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S')

                    conv = lambda i : i or ''

                    priority = row[21]
                    prepared_row = [
                        row[1], # id 
                        row[9], # service_title
                        row[10], # work_category_title
                        row[17], # state 
                        row[0], # description
                        (row[2] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S'), # created_at
                        finished, # finished_at
                        dead_line, # dead_line
                        executed, # executed_at
                        row[5], #rating
                        row[11], # building_full_title
                        row[12], # room_title
                        room_type, # Тип помещения
                        conv(row[15]) + " " + conv(row[13]) + " " + conv(row[14]), # executor_full_name
                        row[16],# company
                        room_title, # parsed_room_title
                        finished_at,# finish_date_plane
                        priority,
                        work_place
                    ]
                    sheet.append(prepared_row)

            ROOT_DIR = os.getcwd()
            file_path = ROOT_DIR + '/reports/issues_report.xlsx'
            workbook.save(file_path)

            return file_path
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    async def get_report_path() -> str:
        ROOT_DIR = os.getcwd()
        file_path = ROOT_DIR + '/reports/issues_report.xlsx'
        
        return file_path

    @staticmethod
    async def get_all_external_ids_by_service(uow: AbstractUnitOfWork, service_ids: list[int] | None = None) -> Sequence[int]:
        async with uow:
            if service_ids is not None:
                res: Sequence[int] = []
                for ser_id in service_ids:
                    ids_by_service =  await uow.issues_repo.get_all_external_ids_filtered(service_id=ser_id)   
                    res.extend(ids_by_service)
                return res
            else:
                return await uow.issues_repo.get_all_external_ids()

    @staticmethod
    async def get_all_external_ids_with_included_statuses(uow: AbstractUnitOfWork, service_id: int, statueses: list[str] = []) -> set[int]:
        async with uow:
            res = await uow.issues_repo.get_all_external_ids_with_included_statuses(service_id, statueses)
            return set(res)

    @staticmethod
    async def get_all_external_ids(uow: AbstractUnitOfWork) -> Sequence[int]:
        async with uow:
            return await uow.issues_repo.get_all_external_ids()

    @staticmethod
    async def get_last_statuses_by_id(uow: AbstractUnitOfWork, issues_id: list[int]) -> dict[int, str]:
        async with uow:
            res = await uow.issues_repo.get_last_statuses_by_id(issues_id)
            
            res_dict = {}
            for iss_row in res:
                res_dict[iss_row[0]] = iss_row[1]
                 
            return res_dict

    @with_uow
    @perfomance_timer
    async def get_filtered_issues(
        self,
        filters: IssuesFiltersSchema
    ) -> FilteredIssuesGetSchema:
        try:
            if filters.transition.statuses == []:
                filters.transition.statuses = await self.uow.statuses_history_repo.get_unique_statuses()

            total_count_cache = await self.redis.get_cache(CachePrefixes.ISSUES, "total")
            if not total_count_cache:
                total_count: int = await self.uow.issues_repo.get_filtered_and(facility_id=2)
                await self.redis.set_cache(CachePrefixes.ISSUES, "total", str(total_count), 600)
            else:
                total_count = int(total_count_cache)

            filtered_issues_count_key = IssuesFiltersSchema.build_cache_key(filters)
            filters_dto: IssueFilterDTO = map_filters_to_dto(filters)
            filtered_count_cache = await self.redis.get_cache(CachePrefixes.ISSUES, filtered_issues_count_key)
            if not filtered_count_cache:
                filtered_count: int = await self.uow.issues_repo.get_count_issues_with_filters_for_report3(
                    filters_dto
                )
                if filtered_count == 0:
                    res = FilteredIssuesGetSchema(
                        filtered_count=0,
                        total_count=total_count,
                        issues=[]
                    )
                    return res
                await self.redis.set_cache(CachePrefixes.ISSUES, filtered_issues_count_key, str(filtered_count), 600)
            else:
                filtered_count = int(filtered_count_cache)

            iss_ids = await self.uow.issues_repo.get_issue_ids_with_filters_for_api_ver3(
                filters_dto
            )
            issues: list[FilteredIssue] = []

            if iss_ids == [] :
                res = FilteredIssuesGetSchema(
                    filtered_count=filtered_count or 0,
                    total_count=total_count,
                    issues=issues
                )
                return res

            rows = await self.uow.issues_repo.get_filtered_issues_for_report_ver4(iss_ids)
            for row in rows:
                end_date = close_date = None

                if row.last_status == "исполнена" or row.last_status == "отказано":
                    end_date = row.last_status_created
                    close_date = None
                elif row.pred_status == "исполнена" and row.last_status == "закрыта" :
                    end_date = row.pred_status_created
                    close_date = row.last_status_created

                # compare_date = end_date if end_date else current_time
                # logger.debug(f"{row.external_id} {row.finish_date_plane.tzinfo}, {compare_date.tzinfo}, ")

                # if row.finish_date_plane and compare_date > row.finish_date_plane:
                #     overdue = "просрочена"
                # else:
                #     overdue = ""

                room_title = row.room_title.split(" ")[0] if row.room_title else ""

                filtered_iss: FilteredIssue = FilteredIssue(
                    id=row.external_id,
                    service_title=row.service_title,
                    wc_title=row.wc_title,
                    iss_descr=row.iss_descr,
                    
                    last_status=row.last_status,

                    created_at_first_stat=row.first_status_created,
                    end_date=end_date,
                    close_date=close_date,
                    finish_date_plan=row.finish_date_plane,

                    rating=row.rating,
                    building_title=row.building_title,
                    room_title=room_title or "",
                    work_place=row.work_place,

                    prior_title=row.prior_title or ""
                )
                issues.append(filtered_iss)

            res = FilteredIssuesGetSchema(
                filtered_count=filtered_count or 0,
                total_count=total_count,
                issues=issues
            )
            return res

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            raise ValueError("Error during getting filtered issues")

    @lru_cache()
    @with_uow
    async def get_count(
        self,
    ) -> int:
        return await self.uow.issues_repo.get_count()

    @lru_cache()
    @with_uow
    async def get_filter_values(
        self,
    ) -> IssueFilters:
        buildings = await self.uow.buildings_repo.get_all()
        services = await self.uow.service_repo.get_all()
        work_categories = await self.uow.work_categories_repo.get_all()
        priorities = await self.uow.priority_repo.get_all()
        statuses = await self.uow.statuses_history_repo.get_unique_statuses()
        services = [ThinDict(id=e.external_id, title=e.title) for e in services]
        services = [service for service in services if service.id not in [20, 21, 22]]
        return IssueFilters(
            buildings=[ThinDict(id=e.id, title=e.title) for e in buildings],
            services=services,
            work_categories=[WorkCat(id=e.id, title=e.title, service_id=e.service_id) for e in work_categories],
            priorities=[ThinDict(id=e.id, title=e.title) for e in priorities],
            statuses=statuses
        )

    @with_uow
    async def bulk_insert_new_issues_with_statuses(self, issues: list[IssuePostSchema], statuses: list[HistoryStatusRecord]) -> int:
        issues_dumped = [e.model_dump() for e in issues]
        statuses_dumped = [e.model_dump() for e in statuses]

        try:
            await self.uow.issues_repo.bulk_insert(issues_dumped)
            await self.uow.statuses_history_repo.bulk_insert(statuses_dumped)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        logger.info(f"Issues between {issues[0].external_id}-{issues[-1].external_id} were inserted with statuses")
        return 0

    @with_uow
    async def bulk_update_issues_with_statuses(self, issues: list[IssuePostSchema], statuses: list[HistoryStatusRecord]) -> int:
        issues_dumped = [e.model_dump() for e in issues]
        statuses_dumped = [e.model_dump() for e in statuses]

        try:
            await self.uow.issues_repo.bulk_update_by_external_ids(issues_dumped)
            if statuses_dumped != []:
                await self.uow.statuses_history_repo.bulk_insert(statuses_dumped)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        logger.info(f"Issues between {issues[0].external_id}-{issues[-1].external_id} were updated with statuses")
        return 0

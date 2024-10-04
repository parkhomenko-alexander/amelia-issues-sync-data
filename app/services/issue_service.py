import os
import traceback
from datetime import datetime, timedelta
from typing import Sequence

from loguru import logger
from openpyxl import Workbook
from sqlalchemy import Row

from app.schemas.issue_schemas import IssuePostSchema
from app.schemas.user_schemas import UserPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class IssueService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
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


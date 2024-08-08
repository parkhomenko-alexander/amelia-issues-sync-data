import os
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
    async def generate_issues_report(self, start_date: datetime, end_date:datetime, hours_delta: int = 0 ):
        """
        Generate issues report
        """
        try:
            result: Sequence[Row] = await self.uow.issues_repo.get_issues_with_filtered_by_time(start_date, end_date)
            workbook = Workbook()
            sheet = workbook.active

            header_order = [
                "id", "service_title", "work_category_title", "state", "description",
                "created_at","finished_at","dead_line","executed_at", "rating", "building_full_title","room_title","Тип помещения","executor_full_name","company","parsed_room_title"
            ]
            
            if sheet != None:
                sheet.append(header_order)

                for row in result:
                # self.model.description,
                # self.model.external_id, 
                # self.model.created_at, 
                # self.model.finish_date_plane, 
                # self.model.dead_line,
                # # finished_at
                # self.model.rating,
                # self.model.tel,
                # self.model.email,
                
                # self.model.company_id, 
                # self.model.service_id,
                # self.model.work_category_id,
                # self.model.building_id,
                # self.model.executor_id, 
                # self.model.room_id 
                # select(filtered_issues_cte, Service.title, WorkCategory.title, Building.title, Room.title, User.first_name, User.middle_name, User.last_name, Company.full_name, last_statuses_with_msg.c.status, last_statuses_with_msg.c.created_at, prelast_statuses_cte.c.created_at, prelast_statuses_cte.c.created_at)
                    room_title_row = row[17] 
                    if " " in room_title_row:
                        room_title, room_type = row[17].split(" ", 1)
                    else:
                        room_title = room_title_row
                        room_type = ""
                    
                    pre_last_status = row[24]
                    last_status = row[22]

                    if last_status == "исполнена":
                        executed = (row[25] + timedelta(10)).strftime('%d.%m.%Y %H:%M:%S') 
                        finished = ""
                    elif pre_last_status == "исполнена" and last_status == "закрыта":
                        executed = (row[25] + timedelta(10)).strftime('%d.%m.%Y %H:%M:%S') 
                        finished = (row[23] + timedelta(10)).strftime('%d.%m.%Y %H:%M:%S')
                    else:
                        executed = ""
                        finished = ""

                    conv = lambda i : i or ''

                    prepared_row = [
                        row[1], # id 
                        row[14], # service_title
                        row[15], # work_category_title
                        row[22], # state 
                        row[0], # description
                        (row[2] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S'), # created_at
                        finished, # finished_at
                        (row[4] + timedelta(hours=10)).strftime('%d.%m.%Y %H:%M:%S'), # dead_line
                        executed, # executed_at
                        row[5], #rating
                        row[16], # building_full_title
                        row[17], # room_title
                        room_type, # Тип помещения
                        conv(row[20]) + " " + conv(row[18]) + " " + conv(row[19]), # executor_full_name
                        row[21],# company
                        room_title# parsed_room_title
                    ]
                    sheet.append(prepared_row)

            ROOT_DIR = os.getcwd()
            file_path = ROOT_DIR + '/reports/issues_report.xlsx'       
            workbook.save(file_path)
        except Exception as e:
            logger.error(e)


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


import os
import traceback
from typing import Sequence
from uuid import uuid4

import xlsxwriter
from loguru import logger
from sqlalchemy import Row

from app.schemas.issue_schemas import IssuesFiltersSchema
from app.services.services_helper import with_uow
from app.utils.redis_manager import CachePrefixes, RedisManager
from app.utils.unit_of_work import AbstractUnitOfWork


class ReportService:
    def __init__(self, uow, redis_manager: RedisManager):
        self.uow = uow
        self.redis_manager = redis_manager


    def split_list_into_three_parts(self, ids):
        third = len(ids) // 3  # Integer division to get one third of the list length
        remainder = len(ids) % 3  # Check if there is a remainder

        # Calculate the split indices
        first_part_end = third + (1 if remainder > 0 else 0)
        second_part_end = 2 * third + (1 if remainder > 1 else 0)

        # Split the list into three parts
        part1 = tuple(ids[:first_part_end])
        part2 = tuple(ids[first_part_end:second_part_end])
        part3 = tuple(ids[second_part_end:])

        return part1, part2, part3

    @with_uow
    async def generate_issues_report_ver2(
        self,
        filters: IssuesFiltersSchema,
        task_id: str
    ) -> str | None:
        await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:status", "processing")

        output_file = await self.get_report_path() + f"/issues_report_{task_id}.xlsx"  # Уникальный файл для задачи
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet("Зявки")
        
        bold_format = workbook.add_format({"bold": True})
        datetime_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm:ss"})

        headers = [
            "id", "сервис", "услуга", "описание",
            "статус",
            "дата создания", "дата исполнения", "дата закрытия", "плановая дата исполнения",
            "оценка", "строение", "помещение", "место проведения", 
            "приоритет", "срочность"
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, bold_format)

        try:

            match filters.transition.statuses:
                case []:
                    statuses = await self.uow.statuses_history_repo.get_unique_statuses()
                case _:
                    statuses = filters.transition.statuses
            
            result_len = 1
            row_ind = 1
            page = filters.pagination.ofset
            ids = await self.uow.issues_repo.get_issue_ids_with_filters_for_report_ver2(
                filters.creation.start_date,
                filters.creation.end_date,
                filters.transition.start_date,
                filters.transition.end_date,
                statuses,
                filters.place.buildings_id,
                filters.work.services_id,
                filters.work.work_categories_id,
                filters.place.rooms_id,
                filters.priorities_id,
                filters.urgency,
            )
            chunks = self.split_list_into_three_parts(ids)

            for chunk in chunks:
                rows: Sequence[Row] = await self.uow.issues_repo.get_filtered_issues_for_report_ver2(
                    chunk
                )

                for row in reversed(rows):
                    if row.last_status == "исполнена":
                        end_date = row.last_status_created
                        close_date = ""
                    elif row.pred_status == "исполнена" and row.last_status == "закрыта" :
                        end_date = row.pred_status_created
                        close_date = row.last_status_created
                    # ! отказано
                    else:
                        end_date = close_date = ""
                    room_title = row.room_title.split(" ")[0] if row.room_title else ""
                    worksheet.write(row_ind, 0, row.external_id)
                    worksheet.write(row_ind, 1, row.service_title)
                    worksheet.write(row_ind, 2, row.wc_title)
                    worksheet.write(row_ind, 3, row.iss_descr)

                    worksheet.write(row_ind, 4, row.last_status)
                    
                    worksheet.write(row_ind, 5, row.first_status_created, datetime_format)
                    worksheet.write(row_ind, 6, end_date, datetime_format)
                    worksheet.write(row_ind, 7, close_date, datetime_format)
                    worksheet.write(row_ind, 8, row.finish_date_plane, datetime_format)


                    worksheet.write(row_ind, 9, row.rating)
                    worksheet.write(row_ind, 10, row.building_title)
                    worksheet.write(row_ind, 11, room_title)
                    worksheet.write(row_ind, 12, row.work_place)

                    worksheet.write(row_ind, 13, row.prior_title)
                    worksheet.write(row_ind, 14, row.urgency)

                    row_ind += 1


            date_column_legth = 20
            worksheet.set_column(5, 5, date_column_legth)
            worksheet.set_column(6, 6, date_column_legth)
            worksheet.set_column(7, 7, date_column_legth)
            worksheet.set_column(8, 8, date_column_legth)

            workbook.close()
            await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:status", "completed")
            await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:file_path", output_file)
            logger.info(f"Report generated: {output_file}")


            return task_id
             
        except Exception as e:
            logger.error(e)
            await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:status", "failed")
            return None
        
    @staticmethod
    async def get_report_path() -> str:
        ROOT_DIR = os.getcwd()
        file_path = ROOT_DIR + '/reports'
        
        return file_path

    async def get_report_status(self, task_id: str) -> dict:
        status = await self.redis_manager.get_cache(CachePrefixes.TASKS_INFO, f"{task_id}:status")
        file_path = await self.redis_manager.get_cache(CachePrefixes.TASKS_INFO, f"{task_id}:file_path")
        return {"status": status, "file_path": file_path}

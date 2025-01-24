import os
import traceback
from datetime import datetime
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
    def __init__(self, uow: AbstractUnitOfWork, redis_manager: RedisManager):
        self.uow = uow
        self.redis_manager = redis_manager


    def split_list_into_three_parts(self, ids):
        third = len(ids) // 3  # Integer division to get one third of the list length
        remainder = len(ids) % 3  # Check if there is a remainder

        # Calculate the split indices
        first_part_end = third + (1 if remainder > 0 else 0)
        second_part_end = 2 * third + (1 if remainder > 1 else 0)

        # Split the list into three parts
        part1 = ids[:first_part_end]
        part2 = ids[first_part_end:second_part_end]
        part3 = ids[second_part_end:]

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

        headers = [
            "id", "сервис", "услуга", "описание",
            "статус",
            "дата создания", "дата исполнения", "дата закрытия", "плановая дата исполнения",
            "оценка", "строение", "помещение", "место проведения", 
            "приоритет", "срочность", "просрочено"
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, bold_format)
        current_time = datetime.now()
        try:

            match filters.transition.statuses:
                case []:
                    statuses = await self.uow.statuses_history_repo.get_unique_statuses()
                case _:
                    statuses = filters.transition.statuses
            
            row_ind = 1
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
                limit = 1000000,
                page = 0,
                current_statuses=filters.current_statuses
            )
            ids = sorted(ids, reverse=True)
            if ids != []:
                
                if len(ids) > 50000:
                    chunks = self.split_list_into_three_parts(ids)
                else:
                    chunks = [ids]

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
                        
                        compare_date = end_date if end_date else current_time

                        if row.finish_date_plane and compare_date > row.finish_date_plane:
                            overdue = "просрочена"
                        else:
                            overdue = ""
                        
                        end_date_formatted = end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else ""
                        close_date_formatted = close_date.strftime('%Y-%m-%d %H:%M:%S') if close_date else ""
                        finish_date_plane_formatted = (
                            row.finish_date_plane.strftime('%Y-%m-%d %H:%M:%S') if row.finish_date_plane else ""
                        )
                        first_status_created_formatted = (
                            row.first_status_created.strftime('%Y-%m-%d %H:%M:%S') if row.first_status_created else ""
                        )
                        
                        room_title = row.room_title.split(" ")[0] if row.room_title else ""
                        worksheet.write(row_ind, 0, row.external_id or "")
                        worksheet.write(row_ind, 1, row.service_title or "")
                        worksheet.write(row_ind, 2, row.wc_title or "")
                        worksheet.write(row_ind, 3, f"'{row.iss_descr}" or "")

                        worksheet.write(row_ind, 4, row.last_status or "")
                        
                        worksheet.write(row_ind, 5, first_status_created_formatted or "")
                        worksheet.write(row_ind, 6, end_date_formatted or "")
                        worksheet.write(row_ind, 7, close_date_formatted or "")
                        worksheet.write(row_ind, 8, finish_date_plane_formatted or "")


                        worksheet.write(row_ind, 9, row.rating or "")
                        worksheet.write(row_ind, 10, row.building_title or "")
                        worksheet.write(row_ind, 11, room_title or "")
                        worksheet.write(row_ind, 12, row.work_place or "")

                        worksheet.write(row_ind, 13, row.prior_title or "")
                        worksheet.write(row_ind, 14, row.urgency or "")
                        worksheet.write(row_ind, 15, overdue or "")

                        row_ind += 1

                date_column_legth = 20
                prior_len = 14
                worksheet.set_column(5, 5, date_column_legth)
                worksheet.set_column(6, 6, date_column_legth)
                worksheet.set_column(7, 7, date_column_legth)
                worksheet.set_column(8, 8, date_column_legth)

                worksheet.set_column(13, 13, prior_len)
                worksheet.set_column(14, 14, prior_len)
                worksheet.set_column(15, 15, prior_len)

            workbook.close()
            await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:status", "completed")
            await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:file_path", output_file)
            logger.info(f"Report generated: {output_file}")


            return task_id
             
        except Exception as e:
            logger.exception(e)
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

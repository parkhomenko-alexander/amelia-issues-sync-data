import os
import traceback
from datetime import datetime
from typing import Sequence
from uuid import uuid4

import xlsxwriter
from loguru import logger
from sqlalchemy import Row

from app.dto.issues_filter_dto import IssueFilterDTO
from app.dto.mappers.issue_filters_mapper import map_filters_to_dto
from app.schemas.issue_schemas import IssuesFiltersSchema
from app.services.services_helper import with_uow
from app.utils.benchmark import perfomance_timer
from app.utils.redis_manager import CachePrefixes, RedisManager
from app.utils.unit_of_work import AbstractUnitOfWork


class ReportService:
    def __init__(self, uow: AbstractUnitOfWork, redis_manager: RedisManager):
        self.uow = uow
        self.redis_manager = redis_manager


    def split_list_into_chunks(self, ids, chunk_size=10):
        chunks = [ids[i:i + chunk_size] for i in range(0, len(ids), chunk_size)]
        return chunks

    @perfomance_timer
    @with_uow
    async def generate_issues_report_ver2(
        self,
        filters: IssuesFiltersSchema,
        task_id: str
    ) -> str | None:
        
        def format_date(dt):
            return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ""

        await self.redis_manager.set_cache(CachePrefixes.TASKS_INFO, f"{task_id}:status", "processing")

        output_file = await self.get_report_path() + f"/issues_report_{task_id}.xlsx"
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
            if filters.transition.statuses == []:
                filters.transition.statuses = await self.uow.statuses_history_repo.get_unique_statuses()

            row_ind = 1
            filters_dto: IssueFilterDTO = map_filters_to_dto(filters)
            
            ids = await self.uow.issues_repo.get_issue_ids_with_filters_for_report_ver3(
                filters_dto
            )
            # ids = sorted(ids, reverse=True)
            if ids != []:

                if len(ids) > 50_000:
                    chunks = self.split_list_into_chunks(ids, chunk_size=20000)
                else:
                    chunks = [ids]

                for chunk in chunks:
                    rows: Sequence[Row] = await self.uow.issues_repo.get_filtered_issues_for_report_ver4(
                        chunk
                    )

                    for row in rows:
                        end_date = close_date = ""
                        
                        if row.last_status == "исполнена"  or row.last_status == "отказано":
                            end_date = row.last_status_created
                            close_date = ""
                        elif row.pred_status == "исполнена" and row.last_status == "закрыта" :
                            end_date = row.pred_status_created
                            close_date = row.last_status_created

                        compare_date = end_date if end_date else current_time
                        # logger.debug(f"{row.external_id} {row.finish_date_plane.tzinfo}, {compare_date.tzinfo}, ")

                        if row.finish_date_plane and compare_date > row.finish_date_plane:
                            overdue = "просрочена"
                        else:
                            overdue = ""

                        room_title = row.room_title.split(" ")[0] if row.room_title else ""
                        worksheet.write(row_ind, 0, row.external_id or "")
                        worksheet.write(row_ind, 1, row.service_title or "")
                        worksheet.write(row_ind, 2, row.wc_title or "")
                        worksheet.write(row_ind, 3, f"'{row.iss_descr}" or "")

                        worksheet.write(row_ind, 4, row.last_status or "")
                        
                        worksheet.write(row_ind, 5, format_date(row.first_status_created))
                        worksheet.write(row_ind, 6, format_date(end_date))
                        worksheet.write(row_ind, 7, format_date(close_date))
                        worksheet.write(row_ind, 8, format_date(row.finish_date_plane))

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

import os
import traceback
from typing import Sequence
from uuid import uuid4

import xlsxwriter
from loguru import logger
from sqlalchemy import Row

from app.schemas.issue_schemas import IssuesFiltersSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class ReportService:
    _instance = None
    uow: AbstractUnitOfWork
    active_reports: dict[str, str]

    def __new__(cls, uow: AbstractUnitOfWork):
        if cls._instance is None:
            cls._instance = super(ReportService, cls).__new__(cls)
            cls._instance.uow = uow
            cls._instance.active_reports = {}
        return cls._instance

    @with_uow
    async def generate_issues_report_ver2(
        self,
        filters: IssuesFiltersSchema,
        task_id: str
    ) -> str | None:
        
        self.active_reports[task_id] = "processing" 
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
            while result_len <= filters.pagination.limit and result_len != 0:
                rows: Sequence[Row] = await self.uow.issues_repo.get_issues_with_filters_for_report_ver2(
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
                    filters.pagination.limit,
                    page
                )

                for row in rows:
                    if row.last_status == "исполнена":
                        end_date = row.created_at_last_stat
                        close_date = ""
                    elif row.predlast_status == "исполнена" and row.last_status == "закрыта" :
                        end_date = row.created_at_predlast_stat
                        close_date = row.created_at_last_stat
                    # ! отказано
                    else:
                        end_date = close_date = ""
                    room_title = row.room_title.split(" ")[0] if row.room_title else ""
                    worksheet.write(row_ind, 0, row.issue_id)
                    worksheet.write(row_ind, 1, row.service_title)
                    worksheet.write(row_ind, 2, row.wc_title)
                    worksheet.write(row_ind, 3, row.iss_descr)

                    worksheet.write(row_ind, 4, row.last_status)
                    
                    worksheet.write(row_ind, 5, row.created_at_first_stat, datetime_format)
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

                result_len = len(rows)
                page += 1

            date_column_legth = 20
            worksheet.set_column(5, 5, date_column_legth)
            worksheet.set_column(6, 6, date_column_legth)
            worksheet.set_column(7, 7, date_column_legth)
            worksheet.set_column(8, 8, date_column_legth)

            workbook.close()
            self.active_reports[task_id] = output_file
            logger.info(f"Report generated: {output_file}")


            return task_id
             
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            self.active_reports[task_id] = "failed"
            return None
        
    @staticmethod
    async def get_report_path() -> str:
        ROOT_DIR = os.getcwd()
        file_path = ROOT_DIR + '/reports'
        
        return file_path

    async def get_report_status(self, task_id: str) -> str | dict[str, str]:
        return self.active_reports.get(task_id, "Task not found")

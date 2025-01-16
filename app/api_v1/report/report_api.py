from datetime import datetime
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from app.api_v1.dependencies import RedisManagerDep, UowDep
from app.api_v1.report.dependencies import validate_dates
from app.schemas.issue_schemas import IssuesFiltersSchema
from app.services.issue_service import IssueService
from app.services.report_service import ReportService
from app.services.room_service import RoomService
from app.utils.redis_manager import RedisManager
from logger import logger

router = APIRouter(
    tags=['Reports']
)


async def file_streamer(file_path: str) -> AsyncGenerator[bytes, None]:
    """Streams file content in chunks."""
    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            yield chunk


@router.get(
    '/general_rooms_report', 
    # response_model=FacilityPostSchema,
    # status_code=status.HTTP_201_CREATED
)
async def generate_general_report(
    uow: UowDep,
    request: Request,
    response_class=FileResponse  
):  
    try:
        room_service = RoomService(uow)
        file_report = await room_service.generate_general_rooms_report()
        return FileResponse(path=file_report, filename="file.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as error:
        logger.error(error)


@router.get(
    '/generate_general_issues_report', 
)
async def issues_report(
    uow: UowDep,
    request: Request,
    dates: tuple[datetime, datetime] = Depends(validate_dates),
):  
    try:
        issue_service = IssueService(uow)
        start_date, end_date  = dates
        file_report = await issue_service.generate_issues_report(start_date, end_date)
        if file_report is None:
            raise HTTPException(status_code=400, detail="Some error")

        return "Start generating issues report"
        # return FileResponse(path=file_report, filename=f"issues-{start_date}-{end_date}.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    except Exception as error:
        logger.error(error)
        return error


@router.get(
    '/save_general_issues_report', 
)
async def save_issues_report(
    uow: UowDep,
):  
    try:
        issue_service = IssueService(uow)
        file_path = await issue_service.get_report_path()
        return FileResponse(path=file_path, filename=f"issues-report.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    except Exception as error:
        logger.error(error)
        return error


@router.post(
    '/generate_general_issues_report_ver2', 
)
async def issues_report_ver2(
    uow: UowDep,
    redis: RedisManagerDep,
    issues_filters: IssuesFiltersSchema,
    background_tasks: BackgroundTasks
):  
    try:
        task_id = str(uuid4())
        logger.info(task_id)

        report_service = ReportService(uow, redis_manager=redis)
        background_tasks.add_task(report_service.generate_issues_report_ver2,issues_filters, task_id)

        return {"task_id": task_id, "status_url": f"/issue-report-file-status/{task_id}"}
        
    except Exception as error:
        logger.error(error)
        return error


@router.get(
    '/issue-report-file-status/{task_id}', 
)
async def get_report(
    uow: UowDep,
    redis: RedisManagerDep,
    task_id:str
):
    report_service = ReportService(uow, redis_manager=redis)
    res = await report_service.get_report_status(task_id)
    status = res["status"]
    match status:
        case "processing":
            return {"status": "processing"}
        case "failed":
            return {"status": "failed"}
        case "completed":
            return StreamingResponse(
                file_streamer(res["file_path"]),
                media_type="application/vnd.ms-excel",
                headers={"Content-Disposition": f"attachment; filename=report.xlsx"}
            )
        case dict():
            return {"error": "Invalid data format"}
        case _:
            return {"error": "Task not found"}

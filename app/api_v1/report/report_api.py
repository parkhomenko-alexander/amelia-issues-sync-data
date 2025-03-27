from typing import AsyncGenerator
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse, StreamingResponse

from app.api_v1.dependencies import RedisManagerDep, UowDep
from app.schemas.issue_schemas import IssuesFiltersSchema
from app.services.report_service import ReportService
from app.services.room_service import RoomService
from app.utils.benchmark import perfomance_timer
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


@perfomance_timer
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
async def get_report_status(
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
            return {"status": "completed"}
        case dict():
            return {"error": "Invalid data format"}
        case _:
            return {"error": "Task not found"}


@router.get(
    '/save-issue-report/{task_id}', 
)
async def save_report(
    uow: UowDep,
    redis: RedisManagerDep,
    task_id:str
):
    report_service = ReportService(uow, redis_manager=redis)
    res = await report_service.get_report_status(task_id)

    return StreamingResponse(
            file_streamer(res["file_path"]),
            media_type="application/vnd.ms-excel",
            headers={"Content-Disposition": f"attachment; filename=report.xlsx"}
        )

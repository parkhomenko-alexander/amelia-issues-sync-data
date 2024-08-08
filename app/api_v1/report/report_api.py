import re
from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse

from app.api_v1.dependencies import UowDep
from app.schemas.issue_schemas import IssueReportDataSchema
from app.services.issue_service import IssueService
from app.services.room_service import RoomService
from logger import logger

router = APIRouter(
    tags=['Reports']
)

datetime_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"

def validate_datetime(date_str: str) -> datetime:
    if not re.match(datetime_regex, date_str):
        raise HTTPException(status_code=400, detail="Invalid datetime format. Expected format: YYYY-MM-DDTHH:MM:SS")
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Expected format: YYYY-MM-DDTHH:MM:SS")

def validate_dates(
    start_date: Annotated[str, Query(example="2024-08-05T12:34:56", description="Please provide a date and time in the format YYYY-MM-DDTHH:MM:SS")],
    end_time: Annotated[str, Query(example="2024-08-07T12:34:56", description="Please provide a date and time in the format YYYY-MM-DDTHH:MM:SS")],
) -> tuple[datetime, datetime]:
    start_date_dt = validate_datetime(start_date)
    end_time_dt = validate_datetime(end_time)
    if end_time_dt < start_date_dt:
        raise HTTPException(status_code=400, detail="end_time cannot be earlier than start_date")
    
    start_date_dt -= timedelta(hours=10)
    end_time_dt -= timedelta(hours=10)
    
    return start_date_dt, end_time_dt 


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
    '/general_issues_report', 
)
async def issues_report(
    uow: UowDep,
    request: Request,
    dates: tuple[datetime, datetime] = Depends(validate_dates)
):  
    try:
        issue_service = IssueService(uow)
        start_date, end_date  = dates
        result = await issue_service.generate_issues_report(start_date, end_date)
        
    except Exception as error:
        logger.error(error)

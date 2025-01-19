import re
from datetime import datetime
from typing import Annotated

from fastapi import HTTPException, Query

from app.schemas.issue_schemas import TransitionStatuses

# RoomServiceDep = Annotated[
#     AbstractUnitOfWork, 
#     Depends(SqlAlchemyUnitOfWork)
# ]\

datetime_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"


def validate_datetime(date_str: str | None) -> datetime | None:
    if isinstance(date_str, str) and not re.match(datetime_regex, date_str):
        raise HTTPException(status_code=400, detail="Invalid datetime format. Expected format: YYYY-MM-DDTHH:MM:SS")
    try:
        if isinstance(date_str, str):
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        else:
            return None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Expected format: YYYY-MM-DDTHH:MM:SS")

def validate_dates(
    creation_start_date: Annotated[str | None, Query(example="2024-08-05T12:34:56", description="Please provide a date and time in the format YYYY-MM-DDTHH:MM:SS")] = None,
    creation_end_time: Annotated[str | None, Query(example="2024-10-07T12:34:56", description="Please provide a date and time in the format YYYY-MM-DDTHH:MM:SS")] = None,
) -> tuple[datetime | None, datetime | None]:
    
    start_date_dt = validate_datetime(creation_start_date)
    end_time_dt = validate_datetime(creation_end_time)
    

    if (isinstance(end_time_dt, datetime) and isinstance(start_date_dt, datetime)) and end_time_dt < start_date_dt:
        raise HTTPException(status_code=400, detail="end_time cannot be earlier than start_date")
    
    # start_date_dt -= timedelta(hours=10)
    # end_time_dt -= timedelta(hours=10)
    
    return start_date_dt, end_time_dt 

def validate_transition_statuses(
    transition_start_date: Annotated[str | None, Query(example="2024-08-05T12:34:56",)] = None,
    transition_end_time: Annotated[str | None, Query(example="2024-10-07T12:34:56",)] = None,
    transition_statuses: Annotated[str | None, Query(example="новая,закрыта,исполнена",)] = None,
) -> TransitionStatuses:
    
    start_date_dt = validate_datetime(transition_start_date)
    end_time_dt = validate_datetime(transition_end_time)
    if (isinstance(end_time_dt, datetime) and isinstance(start_date_dt, datetime)) and end_time_dt < start_date_dt:
        raise HTTPException(status_code=400, detail="end_time cannot be earlier than start_date")
    
    data = {
        "transition_statuses_start_date": transition_start_date,
        "transition_statuses_end_date": transition_end_time,
        "statuses": []
    }

    if not transition_statuses is None:
        data["statuses"] = transition_statuses.split(',')

    
    return TransitionStatuses(
        **data
    )
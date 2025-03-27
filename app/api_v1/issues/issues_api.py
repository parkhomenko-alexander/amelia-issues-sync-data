
from time import time
from fastapi import APIRouter, HTTPException

from app.api_v1.dependencies import RedisManagerDep, UowDep
from app.api_v1.issues.dependencies import FiltersDep
from app.schemas.issue_schemas import FilteredIssuesGetSchema, IssueFilters
from app.services.issue_service import IssueService
from app.utils.benchmark import perfomance_timer
from logger import logger

router = APIRouter(
    tags=['Issues']
)

@perfomance_timer
@router.get(
    '',
    response_model=FilteredIssuesGetSchema
)
async def get_filtered_issues(
    uow: UowDep,
    issues_filters: FiltersDep,
    redis: RedisManagerDep
):
    try:

        issue_service = IssueService(uow, redis)
        res = await issue_service.get_filtered_issues(issues_filters)

        return res

    except Exception as error:
        logger.error(error)
        return HTTPException(status_code=500, detail=error)



@router.get(
    '/filters',
    response_model=IssueFilters,
)
async def get_filters(
    uow: UowDep,
    redis: RedisManagerDep
):
    try:
        issue_service = IssueService(uow, redis)
        res = await issue_service.get_filter_values()
        return res

    except Exception as error:
        logger.error(error)
        return HTTPException(status_code=500, detail=error)

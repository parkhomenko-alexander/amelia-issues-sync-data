
from fastapi import APIRouter

from app.api_v1.dependencies import UowDep
from app.api_v1.issues.dependencies import FiltersDep
from app.schemas.issue_schemas import FilteredIssuesGetSchema, IssueFilters
from app.services.issue_service import IssueService
from logger import logger

router = APIRouter(
    tags=['Issues']
)
 
@router.get(
    '',
    response_model=FilteredIssuesGetSchema
)
async def get_filtered_issues(
    uow: UowDep,
    issues_filters: FiltersDep,
):  
    try:
        issue_service = IssueService(uow)
        res = await issue_service.get_filtered_issues(issues_filters)
        return res
        
    except Exception as error:
        logger.error(error)
        return error


@router.get(
    '/filters',
    response_model=IssueFilters
)
async def get_filters(
    uow: UowDep,
):
    try:
        issue_service = IssueService(uow)
        res = await issue_service.get_filter_values()
        return res
        
    except Exception as error:
        logger.error(error)
        return error

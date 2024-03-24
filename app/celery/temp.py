import asyncio
from re import S
from time import sleep
from typing import Sequence
from fastapi.concurrency import run_until_first_complete
from loguru import logger
from requests import Response
from app.celery.amelia_api_calls import APIGrids, APIRoutes, AmeliaApi
from app.celery.helpers import ReturnTypeFromJsonQuery, ReturnTypePathParams, handle_response_of_json_query, handle_response_of_path_params
from app.celery.tasks.amelia_issues_tasks import sync_archive_statuses, sync_work_categories
from app.repositories import issue_repository
from app.schemas.building_schemas import BuildingPostSchema
from app.schemas.floor_schemas import FloorPostSchema
from app.schemas.issue_schemas import IssuePostSchema
from app.schemas.room_schemas import RoomPostSchema
from app.schemas.status_schemas import HistoryStatusRecord
from app.schemas.user_schemas import UserPostSchema
from app.services.building_service import BuildingService
from app.services.company_service import CompanyService
from app.services.fasility_service import FacilityService
from app.services.floor_service import FloorService
from app.services.history_status_service import HistoryStatusService
from app.services.issue_service import IssueService
from app.services.priority_service import PriorityService
from app.services.room_service import RoomService
from app.services.service_service import ServiceService
from app.services.user_service import UserService
from app.services.work_category_service import WorkCategoryService
from app.services.workflow_service import WorkflowService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork

async def sync_current_issues():
    """
    Get current issues
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    
    company_title_id_mapped: dict[str, int] = await CompanyService.get_title_id_mapping(uow)
    service_work_categories_mapped: dict[int, dict[str, int]] = await ServiceService.get_mapping_service_id_work_categories(uow)
    building_title_id_mapped: dict[str, int] = await BuildingService.get_title_id_mapping(uow)
    priority_title_id_mapped: dict[str, int] = await PriorityService.get_title_id_mapping(uow)
    exucutor_fullname_id_mapped: dict[str, int] = await UserService.get_fullname_id_mapping_by_roles(
        uow, 
        ["admin", "director", "chief_engineer", "dispatcher", "executor", "dispatcher/executor"]
    )
    building_rooms_mapping: dict[str, dict[str, int]] = await BuildingService.get_building_rooms_mapping(uow)
    workflow_extenal_id_id_mapping: dict[int, int] = await WorkflowService.get_external_id_id_mapping(uow)
    users_ids: set[int] = await UserService.get_users_ids(uow)


    all_issues_with_statues: dict[int, str] = await HistoryStatusService.get_external_issues_id_with_status_title(uow)
    
    all_external_ids_issues_seq: Sequence[int] = await IssueService.get_all_external_ids(uow)
    all_external_ids_issues_set: set[int] = set(all_external_ids_issues_seq)

    service_ids = [*service_work_categories_mapped]

    logger.info("Current issues are synchronize")
    try:
        issue_service = IssueService(uow)

        for service_id in service_ids:
            issues_for_inserting: list[IssuePostSchema] = []
            issues_for_updating: list[IssuePostSchema] = []
            issue_id_for_status_sinchronize: list[int] = []
            params = amelia_api.create_json_for_request(APIGrids.CURRENT_ISSUES, service_id=service_id)
            response_for_pages: Response | None = amelia_api.get(APIRoutes.CURRENT_ISSUES_WITH_QUERY, params=params)
            
            if response_for_pages is None:
                msg: str = "Page response for service_id: {service_id} is None"
                logger.error(msg)
                continue

            response_data: ReturnTypeFromJsonQuery[IssuePostSchema] = handle_response_of_json_query(response_for_pages, IssuePostSchema)
            pages: int = amelia_api.get_count_of_pages(response_data)
            for i in range(1, pages):
                logger.info(f"Page: {i}, service: {service_id}")

                params = amelia_api.create_json_for_request(APIGrids.CURRENT_ISSUES, page=i, service_id=service_id)
                response = amelia_api.get(APIRoutes.CURRENT_ISSUES_WITH_QUERY, params=params)

                if response is None:
                    msg = "Current issues response is none"
                    logger.error(msg)
                    return msg
        
                response_data: ReturnTypeFromJsonQuery[IssuePostSchema] = handle_response_of_json_query(response, IssuePostSchema)

                for iss in response_data.data:
                    current_issues_status = all_issues_with_statues.get(iss.external_id, None)

                    # print(iss)
                    state = iss.state
                    building_title = iss.building_title.split("/")[0][:-1]
                    if iss.room_title is None:
                        room_id = None
                    else:
                        room_id = building_rooms_mapping[building_title].get(iss.room_title)
                    
                    # на проде не будет проскакивать, для разработки, чтобы не ловить ошибку
                    if iss.declarer_id not in users_ids: 
                        iss.declarer_id = None
                
                    iss.company_id = None if iss.company_name is None else company_title_id_mapped[iss.company_name]
                    iss.work_category_id = service_work_categories_mapped[iss.service_id][iss.work_category_title]
                    
                    iss.building_id = building_title_id_mapped[building_title]

                    iss.priority_id = None if iss.priority_title is None else priority_title_id_mapped.get(iss.priority_title, None)
                    iss.executor_id = None if iss.executor_full_name is None else exucutor_fullname_id_mapped.get(iss.executor_full_name, None)

                    iss.workflow_id = workflow_extenal_id_id_mapping[iss.workflow_id]
                    iss.room_id = room_id
                    # logger.info(iss)

                    match (current_issues_status, iss.external_id in all_external_ids_issues_set, state == current_issues_status):
                        case (None, False, _):
                            issues_for_inserting.append(iss)
                            issue_id_for_status_sinchronize.append(iss.external_id)
                        case (None, True, _):
                            issues_for_updating.append(iss)
                            issue_id_for_status_sinchronize.append(iss.external_id)
                        case (_, _, True):
                            all_issues_with_statues.pop(iss.external_id)
                            issues_for_updating.append(iss)
                        case (_, _, False):
                            issues_for_updating.append(iss)
                            issue_id_for_status_sinchronize.append(iss.external_id)
                            all_issues_with_statues.pop(iss.external_id)

                if i % 10 == 0:

                    if issues_for_inserting != []:
                        await issue_service.bulk_insert(issues_for_inserting) 
                    if issues_for_updating != []:
                        await issue_service.bulk_update(issues_for_updating)
                    if issue_id_for_status_sinchronize != []:
                        await sync_archive_statuses(issue_id_for_status_sinchronize) 

                    issue_id_for_status_sinchronize = []
                    issues_for_updating = []
                    issues_for_inserting = []

                    all_external_ids_issues_seq = await IssueService.get_all_external_ids(uow)
                    all_external_ids_issues_set = set(all_external_ids_issues_seq)

            if issues_for_inserting != []:
                await issue_service.bulk_insert(issues_for_inserting)
                issues_for_inserting = []
            if issues_for_updating != []:
                await issue_service.bulk_update(issues_for_updating)
                issues_for_updating = []
            if issue_id_for_status_sinchronize != []:
                await sync_archive_statuses(issue_id_for_status_sinchronize)
                issue_id_for_status_sinchronize = []

        issue_id_for_status_sinchronize = [*all_issues_with_statues]
        await sync_archive_statuses(issue_id_for_status_sinchronize)

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Current issues were synchronized")
    return

asd =  asyncio.get_event_loop().run_until_complete(sync_current_issues())

from time import sleep
from typing import Sequence
from requests import Response
from app.schemas.issue_schemas import IssuePostSchema
from app.schemas.priority_schemas import PriorityPostSchema
from app.schemas.service_schemas import ServicePostSchema
from app.schemas.status_schemas import HistoryStatusRecord, StatusPostSchema
from app.schemas.work_category_schemas import WorkCategoryPostSchema
from app.schemas.workflow_schemas import WorkflowPostSchema
from app.services.building_service import BuildingService
from app.services.company_service import CompanyService
from app.services.history_status_service import HistoryStatusService
from app.services.issue_service import IssueService
from app.services.priority_service import PriorityService
from app.services.service_service import ServiceService
from app.services.status_service import StatusService
from app.services.user_service import UserService
from app.services.work_category_service import WorkCategoryService
from app.services.workflow_service import WorkflowService
from logger import logger
from app.celery.amelia_api_calls import APIGrids, APIRoutes, AmeliaApi
from app.celery.celery_app import celery_app
from app.celery.helpers import ReturnTypeFromJsonQuery, ReturnTypePathParams, async_to_sync, handle_response_of_json_query, handle_response_of_path_params
from app.services.fasility_service import FacilityService
from app.utils.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork


@celery_app.task()
@async_to_sync
async def sync_priorities():
    """
    Get priorities
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.PRIORITIES)

    response = amelia_api.get(APIRoutes.PRIORITIES_WITH_QUERY, params=params)
    if response is None:
        msg = "Priority response is none"
        logger.error(msg) 
        return msg
    
    response_data: ReturnTypeFromJsonQuery[PriorityPostSchema] | None = handle_response_of_json_query(response, PriorityPostSchema)
    
    priorities = response_data.data
    # priorities: list[PriorityPostSchema] = [PriorityPostSchema.model_validate(f) for f in priorities_data]
    
    facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

    for p in priorities:
        p.facility_id = facilities_name_id_mapped[p.facility_title]
    
    priority_service = PriorityService(uow)

    external_ids = [priority.external_id for priority in priorities]
    existing_external_ids = await priority_service.get_existing_external_ids(external_ids)
    elements_to_insert = [element for element in priorities if element.external_id not in existing_external_ids]
    element_to_update = [element for element in priorities if element.external_id in existing_external_ids]

    if elements_to_insert != []:
        await priority_service.bulk_insert(elements_to_insert) 
    if element_to_update != []:
        await priority_service.bulk_update(element_to_update) 
    msg = "Priority were synchronized"
    logger.info(msg) 
    return msg

@celery_app.task()
@async_to_sync
async def sync_workflows():
    """
    Get priorities
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.WORKFLOWS)

    response = amelia_api.get(APIRoutes.WORKFLOWS_WITH_QUERY, params=params)
    if response is None:
        msg = "Workflow response is none"
        logger.error(msg) 
        return msg
    response_data: ReturnTypeFromJsonQuery[WorkflowPostSchema] | None = handle_response_of_json_query(response, WorkflowPostSchema)
    
    workflows = response_data.data
    
    workflows_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

    for p in workflows:
        p.facility_id = workflows_name_id_mapped[p.facility_title]
    
    workflows_service = WorkflowService(uow)

    external_ids = [wf.external_id for wf in workflows]
    existing_external_ids = await workflows_service.get_existing_external_ids(external_ids)
    elements_to_insert = [element for element in workflows if element.external_id not in existing_external_ids]
    element_to_update = [element for element in workflows if element.external_id in existing_external_ids]

    if elements_to_insert != []:
        await workflows_service.bulk_insert(elements_to_insert) 
    if element_to_update != []:
        await workflows_service.bulk_update(element_to_update) 
    msg = "Workflows were synchronized"
    logger.info(msg) 
    return msg

@celery_app.task()
@async_to_sync
async def sync_statuses():
    """
    Get statuses
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    workflows_service = WorkflowService(uow)
    status_service = StatusService(uow)

    workflows = await workflows_service.get_all()

    logger.info("Companies are synchronize")
    for wf in workflows:
        wf_external_id = wf.external_id
        url = APIRoutes.statuses_for_workflows(wf_external_id)
        response = amelia_api.get(url)
        if response is None:
            msg = f"Statuses for workflow {wf_external_id} response is none"
            logger.error(msg) 
            return msg
        
        response_data: ReturnTypePathParams[StatusPostSchema] | None = handle_response_of_path_params(response, StatusPostSchema)
        statuses = response_data.data
        for st in statuses:
            st.workflow_id = wf.id
        

        external_ids = [s.external_id for s in statuses]
        existing_external_ids = await status_service.get_existing_external_ids(external_ids)
        elements_to_insert = [element for element in statuses if element.external_id not in existing_external_ids]
        element_to_update = [element for element in statuses if element.external_id in existing_external_ids]

        if elements_to_insert != []:
            await status_service.bulk_insert(elements_to_insert) 
        if element_to_update != []:
            await status_service.bulk_update(element_to_update) 
    msg = "Statuses were synchronized"
    logger.info(msg) 
    return msg

@celery_app.task()
@async_to_sync
async def sync_services():
    """
    Get services
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.SERVICES)
    response: Response | None = amelia_api.get(APIRoutes.SERVICES_WITH_QUERY, params=params)
    if response is None:
        msg = "Services response is none"
        logger.error(msg)
        return msg
    
    response_data: ReturnTypeFromJsonQuery[ServicePostSchema] = handle_response_of_json_query(response, ServicePostSchema)
    pages: int = amelia_api.get_count_of_pages(response_data)
    facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

    logger.info("Services are synchronize")
    try:
        service_service = ServiceService(uow)

        for i in range(1, pages):
            params = amelia_api.create_json_for_request(APIGrids.SERVICES, i)
            response = amelia_api.get(APIRoutes.SERVICES_WITH_QUERY, params=params)

            if response is None:
                msg = "Services response is none"
                logger.error(msg)
                return msg
    
            response_data: ReturnTypeFromJsonQuery[ServicePostSchema] = handle_response_of_json_query(response, ServicePostSchema)

            services: list[ServicePostSchema] = []
            for s in response_data.data:
                s.facility_id = facilities_name_id_mapped[s.facility_title]
                services.append(s)

            external_ids = [e.external_id for e in services]
            existing_external_ids = await service_service.get_existing_external_ids(external_ids)
            elements_to_insert = [element for element in services if element.external_id not in existing_external_ids]
            element_to_update = [element for element in services if element.external_id in existing_external_ids]
            if elements_to_insert != []:
                await service_service.bulk_insert(elements_to_insert) 
            if element_to_update != []:
                await service_service.bulk_update(element_to_update) 

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Services were synchronized")
    return

@celery_app.task()
@async_to_sync
async def sync_work_categories():
    """
    Get work categories
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.WORK_CATEGORIES)
    response: Response | None = amelia_api.get(APIRoutes.WORK_CATEGORIES_WITH_QUERY, params=params)
    if response is None:
        msg = "Work categories response is none"
        logger.error(msg)
        return msg
    
    response_data: ReturnTypeFromJsonQuery[WorkCategoryPostSchema] = handle_response_of_json_query(response, WorkCategoryPostSchema)
    pages: int = amelia_api.get_count_of_pages(response_data)
    facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)
    services_name_id_mapped: dict[str, int] = await ServiceService.get_name_id_mapping(uow)

    logger.info("Work categories are synchronize")
    try:
        work_category_service = WorkCategoryService(uow)

        for i in range(1, pages):
            params = amelia_api.create_json_for_request(APIGrids.WORK_CATEGORIES, i)
            response = amelia_api.get(APIRoutes.WORK_CATEGORIES_WITH_QUERY, params=params)

            if response is None:
                msg = "Work categories response is none"
                logger.error(msg)
                return msg
    
            response_data: ReturnTypeFromJsonQuery[WorkCategoryPostSchema] = handle_response_of_json_query(response, WorkCategoryPostSchema)

            work_categories: list[WorkCategoryPostSchema] = []
            for wc in response_data.data:
                wc.facility_id = facilities_name_id_mapped[wc.facility_title]
                wc.service_id = services_name_id_mapped[wc.service_title]
                work_categories.append(wc)

            external_ids = [e.external_id for e in work_categories]
            existing_external_ids = await work_category_service.get_existing_external_ids(external_ids)
            elements_to_insert = [element for element in work_categories if element.external_id not in existing_external_ids]
            element_to_update = [element for element in work_categories if element.external_id in existing_external_ids]
            if elements_to_insert != []:
                await work_category_service.bulk_insert(elements_to_insert) 
            if element_to_update != []:
                await work_category_service.bulk_update(element_to_update) 

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Services were synchronized")
    return

@celery_app.task()
@async_to_sync
async def sync_archive():
    """
    Get archive
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.ARCHIVE_ISSUES)
    response: Response | None = amelia_api.get(APIRoutes.ARCHIVE_ISSUES_WITH_QUERY, params=params)
    if response is None:
        msg = "Archive issues response is none"
        logger.error(msg)
        return msg
    
    response_data: ReturnTypeFromJsonQuery[IssuePostSchema] = handle_response_of_json_query(response, IssuePostSchema)
    pages: int = amelia_api.get_count_of_pages(response_data)

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
    

    logger.info("Archive issues are synchronize")
    try:
        issue_service = IssueService(uow)

        for i in range(1, pages):
            logger.info(f"Page: {i}")

            params = amelia_api.create_json_for_request(APIGrids.ARCHIVE_ISSUES, i)
            response = amelia_api.get(APIRoutes.ARCHIVE_ISSUES_WITH_QUERY, params=params)

            if response is None:
                msg = "Archive issues response is none"
                logger.error(msg)
                return msg
    
            response_data: ReturnTypeFromJsonQuery[IssuePostSchema] = handle_response_of_json_query(response, IssuePostSchema)

            issues: list[IssuePostSchema] = []
            for iss in response_data.data:
                iss.company_id = None if iss.company_name is None else company_title_id_mapped[iss.company_name]
                iss.work_category_id = service_work_categories_mapped[iss.service_id][iss.work_category_title]
                
                building_title = iss.building_title.split("/")[0][:-1]
                iss.building_id = building_title_id_mapped[building_title]

                iss.priority_id = None if iss.priority_title is None else priority_title_id_mapped.get(iss.priority_title, None)
                iss.executor_id = None if iss.executor_full_name is None else exucutor_fullname_id_mapped.get(iss.executor_full_name, None)

                if iss.room_title is None:
                    room_id = None
                else:
                    room_id = building_rooms_mapping[building_title].get(iss.room_title)
                
                # на проде не будет проскакивать, для разработки, чтобы не ловить ошибку
                if room_id is None or iss.declarer_id not in users_ids: 
                    continue

                iss.workflow_id = workflow_extenal_id_id_mapping[iss.workflow_id]
                iss.room_id = room_id
                issues.append(iss)
                # logger.info(iss)

            external_ids = [e.external_id for e in issues]
            if external_ids == []:
                continue
            existing_external_ids = await issue_service.get_existing_external_ids(external_ids)

            elements_to_insert = [element for element in issues if element.external_id not in existing_external_ids]
            element_to_update = [element for element in issues if element.external_id in existing_external_ids]
            if elements_to_insert != []:
                await issue_service.bulk_insert(elements_to_insert) 
            if element_to_update != []:
                await issue_service.bulk_update(element_to_update)

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Archive issues were synchronized")
    await sync_archive_statuses()
    return


async def insert_history_statuses(statuses: list[HistoryStatusRecord], uow: AbstractUnitOfWork):
    history_status_service = HistoryStatusService(uow)

    external_ids = [e.external_id for e in statuses]
    statuses_existing_external_ids = await history_status_service.get_existing_external_ids(external_ids)
    elements_to_insert = [element for element in statuses if element.external_id not in statuses_existing_external_ids]
    if elements_to_insert != []:
        await history_status_service.bulk_insert(elements_to_insert)

# @celery_app.task()
# @async_to_sync
async def sync_archive_statuses(existing_issues_external_ids: Sequence[int] | None=None):
    """
    Sync history statuses
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    if existing_issues_external_ids is None:
        existing_issues_external_ids = await IssueService.get_all_external_ids(uow)

    logger.info("Issues statuses are synchronize")
    try:
        statuses: list[HistoryStatusRecord] = []
        for i in range(0, len(existing_issues_external_ids)):
            logger.info(f"Issues statuses page: {i}")
            ext_issue_id = existing_issues_external_ids[i]
            params = amelia_api.create_json_for_request(APIGrids.ISSUES_STATUSES, 1, issue_id=ext_issue_id)
            response = amelia_api.get(APIRoutes.ISSUES_STATUSES_WITH_QUERY, params=params)
            sleep(0.4)

            if response is None:
                msg = "Issues history statuses response is none"
                logger.error(msg)
                return msg
            response_statuses_data: ReturnTypeFromJsonQuery[HistoryStatusRecord] = handle_response_of_json_query(response, HistoryStatusRecord)
            
            for resp_status in response_statuses_data.data:
                resp_status.issue_id = ext_issue_id
                statuses.append(resp_status)

            if i % 100 == 0 and i != 0:
                await insert_history_statuses(statuses, uow)
                statuses = []

        if statuses != []:
            await insert_history_statuses(statuses, uow)   
              
    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Issues history statuses were synchronized")
    return
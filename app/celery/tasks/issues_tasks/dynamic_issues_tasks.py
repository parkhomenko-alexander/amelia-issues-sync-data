from asyncio import sleep
from datetime import datetime
from typing import Any


from amelia_api_async import APIGrids, APIRoutes
from app.celery.celery_app import celery_app
from .helpers import (DynamicIssuesResponse, ReturnTypeFromJsonQuery,
                                ServicesMappers, ShortIssue,
                                handle_response_of_json_query, run_async_task)
from amelia_api_async import AmeliaApiAsync
from app.schemas.issue_schemas import IssuePostSchema
from app.schemas.status_schemas import HistoryStatusRecord
from app.services.history_status_service import HistoryStatusService
from app.services.issue_service import IssueService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork
from config import config
from logger import logger




async def sync_history_statuses(issue_ids: list[int], delay: float = config.API_CALLS_DELAY) -> list[HistoryStatusRecord]:
    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApiAsync = AmeliaApiAsync()
    await amelia_api.auth()

    history_status_service = HistoryStatusService(uow)

    statuses: list[HistoryStatusRecord] = []
    try:
        for iss_id in issue_ids:
            page = 1
            while True:
                params = amelia_api.create_json_for_request(APIGrids.ISSUES_STATUSES, page, issue_id=iss_id)
                params = amelia_api.encode_params(params)
                response = await amelia_api.get(APIRoutes.ISSUES_STATUSES_WITH_QUERY, params=params)
            
                if response is None:
                    logger.info("Issues history statuses response is none")
                    return []
                response_statuses_data: ReturnTypeFromJsonQuery[HistoryStatusRecord] = handle_response_of_json_query(response, HistoryStatusRecord)
                response_len = len(response_statuses_data.data)
                sts = ""
                for resp_status in response_statuses_data.data:
                    resp_status.issue_id = iss_id
                    statuses.append(resp_status)
                await sleep(delay)
                if response_len < 20:
                    break
                page += 1
        external_ids = [e.external_id for e in statuses]
        statuses_existing_external_ids = await history_status_service.get_existing_external_ids(external_ids)
        elements_to_insert = [element for element in statuses if element.external_id not in statuses_existing_external_ids]
        logger.info(issue_ids)
        logger.info(external_ids)
        logger.info(statuses_existing_external_ids)
        logger.info([(e.issue_id, e.external_id) for e in elements_to_insert])

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return []
    return elements_to_insert

async def map_issue(iss: IssuePostSchema, mappers: dict) -> IssuePostSchema:
    building_title = iss.building_title.split("/")[0][:-1]
    if iss.room_title is None:
        room_id = None
    else:
        room_id = mappers["building_rooms_mapping"][building_title].get(iss.room_title)
    
    iss.room_id = room_id

    if iss.declarer_id not in mappers["users_ids"]:
        iss.declarer_id = None

    iss.company_id = None if iss.company_name is None else mappers["company_title_id_mapped"][iss.company_name]
    iss.work_category_id = mappers["service_work_categories_mapped"][iss.service_id][iss.work_category_title]
    
    iss.building_id = mappers["building_title_id_mapped"][building_title]

    iss.priority_id = None if iss.priority_title is None else mappers["priority_title_id_mapped"].get(iss.priority_title, None)
    iss.executor_id = None if iss.executor_full_name is None else mappers["executor_fullname_id_mapped"].get(iss.executor_full_name, None)

    iss.workflow_id = mappers["workflow_external_id_id_mapping"][iss.workflow_id]

    return iss

async def sync_issues(issues_id: list[int], delay: float = config.API_CALLS_DELAY):
    amelia_api: AmeliaApiAsync = AmeliaApiAsync()
    await amelia_api.auth()

    uow = SqlAlchemyUnitOfWork()
    mappers: dict[str, Any] = await ServicesMappers.mappers(uow)

    issues_for_inserting: list[IssuePostSchema] = []
    for iss_id in issues_id:
        params = amelia_api.generate_query_params_issues(path=APIGrids.DYNAMIC_ISSUES_CART_INFORMATION)
        query_str = amelia_api.encode_params(params)
        response = await amelia_api.get(APIRoutes.DYNAMIC_ISSUES + "/" + str(iss_id) + "?" + query_str)
        if response and response.status_code == 404:
            continue
        if not response: 
            logger.error(f"Issue {iss_id} request error")
            return []
        iss: IssuePostSchema = IssuePostSchema(**response.json()["data"])
        try:
            mapped_iss = await map_issue(iss, mappers)
        except Exception as er:
            logger.error(f"Wrong mapping for issue {iss.external_id}")
            continue
        issues_for_inserting.append(mapped_iss)
        await sleep(delay)


    return issues_for_inserting

async def sync_issues_dynamic(page: None | int = None, issues_id: list[int] = [], time_range: list[str] = [], delay: float = config.API_CALLS_DELAY):
    start  = datetime.now()
    uow = SqlAlchemyUnitOfWork()
    #? НЕ ЗАБЫТЬ поменять время и заюзать паге каунт 
    amelia_api: AmeliaApiAsync = AmeliaApiAsync()
    await amelia_api.auth()

    issues_service = IssueService(uow)

    logger.info(f"Start issues sync process")

    if issues_id == []:
        if time_range == []:
            tr = amelia_api.check_time_range(time_range)
            if tr == []:
                logger.info("Stop sync process, wrong time range")
        else:
            tr = time_range
        logger.info(f"{tr}")
        url = amelia_api.generate_query_params_issues(path=APIGrids.DYNAMIC_ISSUES, page=1, start_date=tr[0], end_date=tr[1])
        params = amelia_api.encode_params(url)
        logger.info(APIRoutes.DYNAMIC_ISSUES + params)
        dynamic_iss_response = await amelia_api.get(APIRoutes.DYNAMIC_ISSUES + "?" + params)
        if dynamic_iss_response is None:
            logger.error("Dynamic issues response is none.")
            return
        response: DynamicIssuesResponse = DynamicIssuesResponse(**dynamic_iss_response.json())
        if page is None:
            page_count = response.page_count(amelia_api.pagination["per_page"])
        else:
            page_count = page
        issues: list[ShortIssue] = []

        for i in range(1, page_count):
            if len(response.data) == 0: break
            url = amelia_api.generate_query_params_issues(path=APIGrids.DYNAMIC_ISSUES, page=i, start_date=tr[0], end_date=tr[1])
            params = amelia_api.encode_params(url)
            dynamic_iss_response = await amelia_api.get(APIRoutes.DYNAMIC_ISSUES + "?" + params)

            if dynamic_iss_response is None:
                logger.error("Dynamic issues response is none.")
                return

            response = DynamicIssuesResponse[ShortIssue](**dynamic_iss_response.json())
            issues.extend(response.data)
        issues_id = [iss.id for iss in issues]

        existed_issues_with_statuses = await issues_service.get_last_statuses_by_id(uow, issues_id)

        issues_id_for_inserting = list(set([sh_iss.id for sh_iss in issues if sh_iss.id not in existed_issues_with_statuses]))
        issues_id_for_updating = list(set([sh_iss.id for sh_iss in issues if sh_iss.id in existed_issues_with_statuses and sh_iss.state != existed_issues_with_statuses[sh_iss.id]]))
    else:
        existed_issues_with_statuses = await issues_service.get_last_statuses_by_id(uow, issues_id)
        issues_id_for_inserting = list(set([iss_id for iss_id in issues_id if iss_id not in existed_issues_with_statuses]))
        issues_id_for_updating = list(set([iss_id for iss_id in issues_id if iss_id in existed_issues_with_statuses]))

    logger.info(f"For insert: {len(issues_id_for_inserting)}, for update: {len(issues_id_for_updating)}")
    
    if issues_id_for_inserting != []:
        logger.info(f"Sync new issues, start {issues_id_for_inserting[0]}")
        mapped_iss = await sync_issues(issues_id_for_inserting, delay)
        statuses = await sync_history_statuses([ms.external_id for ms in mapped_iss])
        if mapped_iss != [] and statuses != []:
            await issues_service.bulk_insert_new_issues_with_statuses(mapped_iss, statuses)

    if issues_id_for_updating != []:
        logger.info(f"Sync existed issues, start {issues_id_for_updating[0]}")
        mapped_iss = await sync_issues(issues_id_for_updating, delay)
        statuses = await sync_history_statuses([ms.external_id for ms in mapped_iss])
        if mapped_iss != []:
            await issues_service.bulk_update_issues_with_statuses(mapped_iss, statuses)

    logger.info(f"Was inserted: {len(issues_id_for_inserting)}, updated: {len(issues_id_for_updating)}")

    end = datetime.now()
    duration_in_minutes = (end - start).total_seconds() / 60
    logger.info(f"Issues sync task successfylly completed. " + f"{duration_in_minutes} minutes")

@celery_app.task
@run_async_task
async def call_dynamic_issues(page: None | int = None, issues_id: list[int] = [], time_range: list[str] = [], delay: float = config.API_CALLS_DELAY):
    delay = config.API_CALLS_DELAY

    await sync_issues_dynamic(page, issues_id, time_range, delay)
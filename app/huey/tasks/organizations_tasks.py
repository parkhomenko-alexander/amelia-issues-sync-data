from asyncio import sleep

from huey import crontab
from app.huey.huey_app import huey

from app.huey.amelia_api_async import APIGrids, APIRoutes, AmeliaApiAsync
from app.huey.helpers import run_async_task
from app.schemas.company_schemas import CompanyPostSchema
from app.schemas.facility_schemas import FacilityPostSchema
from app.schemas.priority_schemas import PriorityPostSchema
from app.schemas.user_schemas import UserPostSchema
from app.schemas.workflow_schemas import WorkflowPostSchema
from app.services.company_service import CompanyService
from app.services.fasility_service import FacilityService
from app.services.priority_service import PriorityService
from app.services.user_service import UserService
from app.services.workflow_service import WorkflowService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork
from config import config
from logger import logger


# @celery_app.task
# @async_to_sync
# async def sync_ficilities():
#     """
#         Get facilities
#     """
#     uow = SqlAlchemyUnitOfWork()

#     amelia_api: AmeliaApi = AmeliaApi()
#     amelia_api.auth()

#     params = amelia_api.create_json_for_request(APIGrids.FACILITIES)

#     response = amelia_api.get(APIRoutes.FACILITIES_WITH_QUERY, params=params)
#     if response is None:
#         msg = "Facility response is none"
#         logger.error(msg) 
#         return msg
    
#     response_data: ReturnTypeFromJsonQuery[FacilityPostSchema] | None = handle_response_of_json_query(response, FacilityPostSchema)
    
#     facilities_data = response_data.data
#     facilities: list[FacilityPostSchema] = [FacilityPostSchema.model_validate(f) for f in facilities_data]
    
#     facility_service = FacilityService(uow)

#     external_ids = [company.external_id for company in facilities]
#     existing_external_ids = await facility_service.get_existing_external_ids(external_ids)
#     elements_to_insert = [element for element in facilities if element.external_id not in existing_external_ids]
#     element_to_update = [element for element in facilities if element.external_id in existing_external_ids]

#     if elements_to_insert != []:
#         await facility_service.bulk_insert(elements_to_insert) 
#     if element_to_update != []:
#         await facility_service.bulk_update(element_to_update) 
#     msg = "Facilities were synchronized"
#     logger.info(msg) 
#     return msg

# @celery_app.task
# @async_to_sync
# async def sync_companies():
#     """
#         Get companies
#     """
#     uow = SqlAlchemyUnitOfWork()
    
#     amelia_api = AmeliaApi()
#     amelia_api.auth()

#     params = amelia_api.create_json_for_request(APIGrids.COMPANIES)

#     response: Response | None = amelia_api.get(APIRoutes.COMPANIES_WITH_QUERY, params=params)
#     if response is None:
#         msg = "Companies response is none"
#         logger.error(msg)
#         return msg

#     response_data: ReturnTypeFromJsonQuery[CompanyPostSchema] = handle_response_of_json_query(response, CompanyPostSchema)
   
#     pages: int = amelia_api.get_count_of_pages(response_data)
#     facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

#     logger.info("Companies are synchronize")
#     try:
#         company_service = CompanyService(uow)

#         for i in range(1, pages):
#             params = amelia_api.create_json_for_request(APIGrids.COMPANIES, i)
#             response = amelia_api.get(APIRoutes.COMPANIES_WITH_QUERY, params=params)

#             if response is None:
#                 msg = "Companies response is none"
#                 logger.error(msg)
#                 return msg
    
#             response_data: ReturnTypeFromJsonQuery[CompanyPostSchema] = handle_response_of_json_query(response, CompanyPostSchema)

#             companies: list[CompanyPostSchema] = []
#             for company in response_data.data:
#                 company.facility_id = facilities_name_id_mapped[company.facility_title]
#                 companies.append(company)

#             external_ids = [company.external_id for company in companies]
#             existing_external_ids = await company_service.get_existing_external_ids(external_ids)
#             elements_to_insert = [element for element in companies if element.external_id not in existing_external_ids]
#             element_to_update = [element for element in companies if element.external_id in existing_external_ids]
#             print(elements_to_insert, element_to_update)
#             if elements_to_insert != []:
#                 await company_service.bulk_insert(elements_to_insert) 
#             if element_to_update != []:
#                 await company_service.bulk_update(element_to_update) 

#     except Exception as e:
#         logger.exception(f"Some error occurred: {e}")
#         return e
    
#     logger.info("Companies were synchronized")
#     return

# @celery_app.task
# @async_to_sync
# async def sync_priorities():
#     """
#     Get priorities
#     """

#     uow = SqlAlchemyUnitOfWork()

#     amelia_api: AmeliaApi = AmeliaApi()
#     amelia_api.auth()

#     params = amelia_api.create_json_for_request(APIGrids.PRIORITIES)

#     response = amelia_api.get(APIRoutes.PRIORITIES_WITH_QUERY, params=params)
#     if response is None:
#         msg = "Priority response is none"
#         logger.error(msg) 
#         return msg
    
#     response_data: ReturnTypeFromJsonQuery[PriorityPostSchema] | None = handle_response_of_json_query(response, PriorityPostSchema)
    
#     priorities = response_data.data
#     # priorities: list[PriorityPostSchema] = [PriorityPostSchema.model_validate(f) for f in priorities_data]
    
#     facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

#     for p in priorities:
#         p.facility_id = facilities_name_id_mapped[p.facility_title]
    
#     priority_service = PriorityService(uow)

#     external_ids = [priority.external_id for priority in priorities]
#     existing_external_ids = await priority_service.get_existing_external_ids(external_ids)
#     elements_to_insert = [element for element in priorities if element.external_id not in existing_external_ids]
#     element_to_update = [element for element in priorities if element.external_id in existing_external_ids]

#     if elements_to_insert != []:
#         await priority_service.bulk_insert(elements_to_insert) 
#     if element_to_update != []:
#         await priority_service.bulk_update(element_to_update) 
#     msg = "Priority were synchronized"
#     logger.info(msg) 
#     return msg

# @celery_app.task
# @async_to_sync
# async def sync_workflows():
#     """
#     Get priorities
#     """

#     uow = SqlAlchemyUnitOfWork()

#     amelia_api: AmeliaApi = AmeliaApi()
#     amelia_api.auth()

#     params = amelia_api.create_json_for_request(APIGrids.WORKFLOWS)

#     response = amelia_api.get(APIRoutes.WORKFLOWS_WITH_QUERY, params=params)
#     if response is None:
#         msg = "Workflow response is none"
#         logger.error(msg) 
#         return msg
#     response_data: ReturnTypeFromJsonQuery[WorkflowPostSchema] | None = handle_response_of_json_query(response, WorkflowPostSchema)
    
#     workflows = response_data.data
    
#     workflows_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

#     for p in workflows:
#         p.facility_id = workflows_name_id_mapped[p.facility_title]
    
#     workflows_service = WorkflowService(uow)

#     external_ids = [priority.external_id for priority in workflows]
#     existing_external_ids = await workflows_service.get_existing_external_ids(external_ids)
#     elements_to_insert = [element for element in workflows if element.external_id not in existing_external_ids]
#     element_to_update = [element for element in workflows if element.external_id in existing_external_ids]

#     if elements_to_insert != []:
#         await workflows_service.bulk_insert(elements_to_insert) 
#     if element_to_update != []:
#         await workflows_service.bulk_update(element_to_update) 
#     msg = "Workflows were synchronized"
#     logger.info(msg) 
#     return msg

# @celery_app.task
# @async_to_sync
# async def sync_users():
#     """
#     Sync users
#     """

#     uow = SqlAlchemyUnitOfWork()

#     amelia_api: AmeliaApi = AmeliaApi()
#     amelia_api.auth()

#     params = amelia_api.create_json_for_request(APIGrids.USERS)
#     response: Response | None = amelia_api.get(APIRoutes.USERS_WITH_QUERY, params=params)
#     if response is None:
#         msg = "Users response is none"
#         logger.error(msg)
#         return msg
    
#     response_data: ReturnTypeFromJsonQuery[UserPostSchema] = handle_response_of_json_query(response, UserPostSchema)
#     pages: int = amelia_api.get_count_of_pages(response_data)

#     company_title_id_mapped: dict[str, int] = await CompanyService.get_title_id_mapping(uow)
#     facility_title_id_mapping: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

#     logger.info("Users are synchronize")
#     try:
#         user_service = UserService(uow)

#         for i in range(1, pages):
#             params = amelia_api.create_json_for_request(APIGrids.USERS, i)
#             response = amelia_api.get(APIRoutes.USERS_WITH_QUERY, params=params)
            
#             if response is None:
#                 msg = "Users response is none"
#                 logger.error(msg)
#                 return msg
    
#             response_data: ReturnTypeFromJsonQuery[UserPostSchema] = handle_response_of_json_query(response, UserPostSchema)

#             users: list[UserPostSchema] = []
#             for user in response_data.data:
#                 if user.external_id == 27:
#                     user.facility_id = facility_title_id_mapping["ДВФУ"]
#                     user.company_id = company_title_id_mapped["ДВФУ"]
#                     users.append(user)
#                     continue
#                 user.facility_id = facility_title_id_mapping[user.facilities]
#                 user.company_id = company_title_id_mapped[user.company_name]    
#                 users.append(user)



#             external_ids = [e.external_id for e in users]
#             existing_external_ids = await user_service.get_existing_external_ids(external_ids)

#             elements_to_insert = [element for element in users if element.external_id not in existing_external_ids]
#             element_to_update = [element for element in users if element.external_id in existing_external_ids]
#             if elements_to_insert != []:
#                 await user_service.bulk_insert(elements_to_insert) 
#             if element_to_update != []:
#                 await user_service.bulk_update(element_to_update) 

#     except Exception as e:
#         logger.exception(f"Some error occurred: {e}")
#         return e
    
#     logger.info("Users were synchronized")
#     return


@huey.task()
@run_async_task
async def patch_common_users(pages: int = 1, delay: float = config.API_CALLS_DELAY):
    amelia_api: AmeliaApiAsync = AmeliaApiAsync()
    await amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.USERS, role="user")
    params = amelia_api.encode_params(params)

    response = await amelia_api.get(APIRoutes.USERS_WITH_QUERY, params=params)
    if response is None:
        msg = "Users response is none"
        logger.error(msg)
        return msg
    
    logger.info("Common users patch")
    users_count = 0
    try:

        for i in range(1, pages):
            params = amelia_api.create_json_for_request(APIGrids.USERS, i, role="user")
            params = amelia_api.encode_params(params)
            response = await amelia_api.get(APIRoutes.USERS_WITH_QUERY, params=params)

            if response is None:
                msg = "Common users patch response is none"
                logger.error(msg)
                return msg

            users = response.json()["data"]
            for user in users:
                user_id = user["id"]

                data = {
                    "user": {
                        "service_id": 19,
                        "company_id": 2
                    }
                }
                url = f"/{user_id}"

                response = await amelia_api.patch(APIRoutes.USERS + url, params=data)
                users_count += 1
                await sleep(delay)
                if users_count % 100 == 0:
                    logger.info(f"{users_count} users patched")
                    

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Common users patch finished")
    return
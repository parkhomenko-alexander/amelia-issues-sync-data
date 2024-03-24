from loguru import logger
from requests import Response
from app.celery.amelia_api_calls import APIGrids, APIRoutes, AmeliaApi
from app.celery.helpers import ReturnTypeFromJsonQuery, async_to_sync, handle_response_of_json_query
from app.schemas.building_schemas import BuildingPostSchema
from app.schemas.floor_schemas import FloorPostSchema
from app.services.building_service import BuildingService
from app.services.fasility_service import FacilityService
from app.services.floor_service import FloorService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork
from app.celery.celery_app import celery_app

@celery_app.task()
@async_to_sync
async def sync_buildings():
    """
    Get buildings
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.BUILDINGS)
    response: Response | None = amelia_api.get(APIRoutes.BUILDINGS_WITH_QUERY, params=params)
    if response is None:
        msg = "Buildings response is none"
        logger.error(msg)
        return msg
    
    response_data: ReturnTypeFromJsonQuery[BuildingPostSchema] = handle_response_of_json_query(response, BuildingPostSchema)
    pages: int = amelia_api.get_count_of_pages(response_data)
    facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

    logger.info("Buildings are synchronize")
    try:
        building_service = BuildingService(uow)

        for i in range(1, pages):
            params = amelia_api.create_json_for_request(APIGrids.BUILDINGS, i)
            response = amelia_api.get(APIRoutes.BUILDINGS_WITH_QUERY, params=params)

            if response is None:
                msg = "Buildings response is none"
                logger.error(msg)
                return msg
    
            response_data: ReturnTypeFromJsonQuery[BuildingPostSchema] = handle_response_of_json_query(response, BuildingPostSchema)

            buildings: list[BuildingPostSchema] = []
            for building in response_data.data:
                building.facility_id = facilities_name_id_mapped[building.facility_title]
                buildings.append(building)

            external_ids = [e.external_id for e in buildings]
            existing_external_ids = await building_service.get_existing_external_ids(external_ids)
            elements_to_insert = [element for element in buildings if element.external_id not in existing_external_ids]
            element_to_update = [element for element in buildings if element.external_id in existing_external_ids]
            if elements_to_insert != []:
                await building_service.bulk_insert(elements_to_insert) 
            if element_to_update != []:
                await building_service.bulk_update(element_to_update) 

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Buildings were synchronized")
    return

@celery_app.task()
@async_to_sync
async def sync_floors():
    """
    Get floors
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    params = amelia_api.create_json_for_request(APIGrids.FLOORS)
    response: Response | None = amelia_api.get(APIRoutes.FLOORS_WITH_QUERY, params=params)
    if response is None:
        msg = "Floors response is none"
        logger.error(msg)
        return msg
    
    response_data: ReturnTypeFromJsonQuery[FloorPostSchema] = handle_response_of_json_query(response, FloorPostSchema)
    pages: int = amelia_api.get_count_of_pages(response_data)

    facilities_title_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)
    building_title_id_mapped: dict[str, int] = await BuildingService.get_title_id_mapping(uow)

    logger.info("Floors are synchronize")
    try:
        floor_service = FloorService(uow)

        for i in range(1, pages):
            params = amelia_api.create_json_for_request(APIGrids.FLOORS, i)
            response = amelia_api.get(APIRoutes.FLOORS_WITH_QUERY, params=params)

            if response is None:
                msg = "Floors response is none"
                logger.error(msg)
                return msg
    
            response_data: ReturnTypeFromJsonQuery[FloorPostSchema] = handle_response_of_json_query(response, FloorPostSchema)

            floors: list[FloorPostSchema] = []
            for floor in response_data.data:
                floor.facility_id = facilities_title_id_mapped[floor.facility_title]
                floor.building_id = building_title_id_mapped[floor.building_title]

                floors.append(floor)

            external_ids = [e.external_id for e in floors]
            existing_external_ids = await floor_service.get_existing_external_ids(external_ids)

            elements_to_insert = [element for element in floors if element.external_id not in existing_external_ids]
            element_to_update = [element for element in floors if element.external_id in existing_external_ids]
            if elements_to_insert != []:
                await floor_service.bulk_insert(elements_to_insert) 
            if element_to_update != []:
                await floor_service.bulk_update(element_to_update) 

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Floors were synchronized")
    return



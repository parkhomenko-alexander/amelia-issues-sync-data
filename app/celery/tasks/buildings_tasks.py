from time import sleep

from loguru import logger
from requests import Response

from app.celery.amelia_api_calls import AmeliaApi, APIGrids, APIRoutes
from app.celery.celery_app import celery_app
from app.celery.helpers import (ReturnTypeFromJsonQuery, async_to_sync,
                                handle_response_of_json_query,
                                handle_response_of_tech_passports)
from app.schemas.building_schemas import BuildingPostSchema
from app.schemas.floor_schemas import FloorPostSchema
from app.schemas.room_schemas import RoomPostSchema
from app.schemas.tech_passport_schemas import TechPassportPostSchema
from app.services.building_service import BuildingService
from app.services.company_service import CompanyService
from app.services.fasility_service import FacilityService
from app.services.floor_service import FloorService
from app.services.room_service import RoomService
from app.services.tech_passport_service import TechPassportService
from app.utils.unit_of_work import SqlAlchemyUnitOfWork
from config import config


@celery_app.task
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

@celery_app.task
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

@celery_app.task
@async_to_sync
async def sync_rooms(delay: float=config.API_CALLS_DELAY, building_id: int | None = None):
    """
        Get rooms
    """

    uow = SqlAlchemyUnitOfWork()

    amelia_api: AmeliaApi = AmeliaApi()
    amelia_api.auth()

    building_ext_id_id_mapped: dict[int, int] = await BuildingService.get_external_id_mapping(uow)
    if building_id:
        building_id_for_rooms: int | None = building_ext_id_id_mapped.get(building_id)
    else:
        building_id_for_rooms = None
    params = amelia_api.create_json_for_request(APIGrids.ROOMS, building_id=building_id)
    response: Response | None = amelia_api.get(APIRoutes.ROOMS_WITH_QUERY, params=params)
    if response is None:
        msg = "Rooms response is none"
        logger.error(msg)
        return msg
    
    response_data: ReturnTypeFromJsonQuery[RoomPostSchema] = handle_response_of_json_query(response, RoomPostSchema)
    pages: int = amelia_api.get_count_of_pages(response_data)
    floors_ext_id_id_mapped: dict[int, int] = await FloorService.get_external_id_mapping(uow)
    facilities_name_id_mapped: dict[str, int] = await FacilityService.get_title_id_mapping(uow)

    logger.info("Rooms are synchronize")
    try:
        room_service = RoomService(uow)
        if building_id_for_rooms:
            rooms_ids: set[int] = set(await room_service.rooms_ids(uow, [building_id_for_rooms]))
        else:
            rooms_ids: set[int] = set(await room_service.rooms_ids(uow,))
            
        for i in range(1, pages):
            params = amelia_api.create_json_for_request(APIGrids.ROOMS, i, building_id=building_id)
            response = amelia_api.get(APIRoutes.ROOMS_WITH_QUERY, params=params)
            sleep(delay)
            if response is None:
                msg = "Rooms response is none"
                logger.error(msg)
                return msg
    
            response_data = handle_response_of_json_query(response, RoomPostSchema)

            rooms: list[RoomPostSchema] = []
            for s in response_data.data:
                s.building_id = building_ext_id_id_mapped[s.building_id]
                s.floor_id = floors_ext_id_id_mapped[s.floor_id]
                s.facility_id = facilities_name_id_mapped[s.facility_title]
                rooms_ids.discard(s.external_id)
                rooms.append(s)

            external_ids = [e.external_id for e in rooms]
            existing_external_ids = await room_service.get_existing_external_ids(external_ids)
            elements_to_insert = [element for element in rooms if element.external_id not in existing_external_ids]
            element_to_update = [element for element in rooms if element.external_id in existing_external_ids]
            if elements_to_insert != []:
                await room_service.bulk_insert(elements_to_insert) 
            if element_to_update != []:
                await room_service.bulk_update(element_to_update)

        if rooms_ids != []:
            await room_service.bulk_delete(list(rooms_ids))
    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Rooms were synchronized")
    return

@celery_app.task
@async_to_sync
async def sync_tech_passports(delay: float = config.API_CALLS_DELAY, building_ids: list[int] | None = None):
    """
        Get tech passports
    """
    uow = SqlAlchemyUnitOfWork()
    
    amelia_api = AmeliaApi()
    amelia_api.auth()

    if building_ids:
        rooms_ids = await RoomService.rooms_ids(uow, building_ids=building_ids)
    else:
        rooms_ids = await RoomService.rooms_ids(uow)

    ids_len = len(rooms_ids)

    logger.info("Tech passports are synchronize")
    try:
        tech_passport_service = TechPassportService(uow)
        tech_passports: list[TechPassportPostSchema] = []
        for i in range(0, ids_len):
            room_id = rooms_ids[i]
            response = amelia_api.get(APIRoutes.TECH_PASSPORT_WITH_ID + str(room_id))
            sleep(delay)
            if response is None:
                continue
            
            tech_passport_validated: TechPassportPostSchema = handle_response_of_tech_passports(response, TechPassportPostSchema, room_id)
            tech_passports.append(tech_passport_validated)

            if i % 50 == 0 and i != 0:
                logger.info(f"Sync {i} tech passports")

            if i != 0 and (i % 50 == 0 or i == ids_len - 1):
                elements_to_insert, elements_to_update = [], []
                external_ids = [tech_passport.external_id for tech_passport in tech_passports]
                existing_external_ids = await tech_passport_service.get_existing_external_ids(external_ids)
                for tech_passport in tech_passports:
                    if tech_passport.external_id in existing_external_ids:
                        elements_to_update.append(tech_passport)
                    else:
                        elements_to_insert.append(tech_passport)

                if elements_to_insert != []:
                    await tech_passport_service.bulk_insert(elements_to_insert) 
                if elements_to_update != []:
                    await tech_passport_service.bulk_update(elements_to_update)
                tech_passports = []

    except Exception as e:
        logger.exception(f"Some error occurred: {e}")
        return e
    
    logger.info("Tech passport were synchronized")
    return
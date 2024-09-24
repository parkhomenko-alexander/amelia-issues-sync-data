from app.celery.celery_app import celery_app
from app.celery.helpers import async_to_sync
from app.services.building_service import BuildingService
from app.services.room_service import RoomService
from app.utils.redis_manager import CachePrefixes, RedisManager
from app.utils.unit_of_work import SqlAlchemyUnitOfWork


@celery_app.task
@async_to_sync
async def update_building_cache():
    uow: SqlAlchemyUnitOfWork = SqlAlchemyUnitOfWork()

    building_external_id_title_mapping = await BuildingService.get_external_id_title_mapping(uow)
    building_title_external_id_mapping = await BuildingService.get_title_external_id_mapping(uow)

    rooms_title_external_id_mapping = await RoomService.get_title_external_id_mapping(uow)
    rooms_title_external_id_mapping = await RoomService.get_external_id_title_mapping(uow)


    redis_manager: RedisManager = RedisManager()
    
    await redis_manager.set_cache(CachePrefixes.BUILDINGS_EXTERNAL_ID_TITLE, building_external_id_title_mapping)
    await redis_manager.set_cache(CachePrefixes.BUILDINGS_TITLE_EXTERNAL_ID, building_title_external_id_mapping)

    await redis_manager.set_cache(CachePrefixes.ROOMS_EXTERNAL_ID_TITLE, rooms_title_external_id_mapping)
    await redis_manager.set_cache(CachePrefixes.ROOMS_TITLE_EXTERNAL_ID, rooms_title_external_id_mapping)

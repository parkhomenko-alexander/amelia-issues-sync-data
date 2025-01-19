from loguru import logger

from app.celery.celery_app import celery_app
from app.celery.helpers import async_to_sync
from app.schemas.building_schemas import BuildingsForCache
from app.services.building_service import BuildingService
from app.services.room_service import RoomService
from app.utils.redis_manager import CachePrefixes, RedisManager
from app.utils.unit_of_work import SqlAlchemyUnitOfWork


@celery_app.task
@async_to_sync
async def update_building_cache():
    try:
        uow: SqlAlchemyUnitOfWork = SqlAlchemyUnitOfWork()
        buildings_structure: BuildingsForCache = await BuildingService.prepare_building_sturcture_for_cache(uow)
        serialized_buildings: str = await BuildingService.serialize_buildings_for_cache(buildings_structure)

        redis_manager: RedisManager = RedisManager()

        await redis_manager.set_cache(CachePrefixes.BUILDINGS_ROOMS_INFO, serialized_buildings)
      
    except Exception as er:
        logger.error(f"Some error: {er}")

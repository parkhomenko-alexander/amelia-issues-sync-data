from loguru import logger

from app.celery.celery_app import celery_app
from app.celery.tasks.issues_tasks.helpers import run_async_task
from app.schemas.building_schemas import BuildingsForCache
from app.services.building_service import BuildingService
from app.utils.redis_manager import CachePrefixes, RedisManager
from app.utils.unit_of_work import SqlAlchemyUnitOfWork


@celery_app.task
@run_async_task
async def update_building_cache():
    try:
        uow: SqlAlchemyUnitOfWork = SqlAlchemyUnitOfWork()
        buildings_structure: BuildingsForCache = await BuildingService.prepare_building_sturcture_for_cache(uow)
        serialized_buildings: str = await BuildingService.serialize_buildings_for_cache(buildings_structure)

        redis_manager: RedisManager = RedisManager()

        await redis_manager.set_cache(CachePrefixes.BUILDINGS_ROOMS_INFO, serialized_buildings)
      
    except Exception as er:
        logger.error(f"Some error: {er}")

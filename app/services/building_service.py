from json import dumps

from loguru import logger

from app.schemas.building_schemas import (BuildingForCache, BuildingPostSchema,
                                          BuildingsForCache)
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class BuildingService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @with_uow
    async def bulk_insert(self, elements_post: list[BuildingPostSchema]) -> int:
        """
        Buildings inserting
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.buildings_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Buildings between {elements_post[0].external_id}-{elements_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, elements_update: list[BuildingPostSchema]) -> int:
        """
        Buildings updating
        """
        elements_data_for_updating = [e.model_dump() for e in elements_update]
        try:
            await self.uow.buildings_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Buildings between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0                 

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.buildings_repo.get_existing_external_ids(ids)

    @staticmethod
    async def get_title_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            buildings = await uow.buildings_repo.get_all()
            buildings_title_id_mapped: dict[str, int] = {}
            for b in buildings:
                buildings_title_id_mapped[b.title] = b.id
            return buildings_title_id_mapped

    @staticmethod
    async def get_title_external_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            buildings = await uow.buildings_repo.get_all()
            buildings_title_external_id_mapped: dict[str, int] = {}
            for b in buildings:
                buildings_title_external_id_mapped[b.title] = b.external_id
            return buildings_title_external_id_mapped

    @staticmethod
    async def get_external_id_title_mapping(uow: AbstractUnitOfWork) -> dict[int, str]:
        async with uow:
            buildings = await uow.buildings_repo.get_all()
            buildings_title_id_mapped: dict[int, str] = {}
            for b in buildings:
                buildings_title_id_mapped[b.external_id] = b.title
            return buildings_title_id_mapped
    
    @staticmethod
    async def get_external_id_mapping(uow: AbstractUnitOfWork) -> dict[int, int]:
        async with uow:
            res = await uow.buildings_repo.get_all()
            mapping = {}
            for f in res:
                mapping[f.external_id] = f.id

            return mapping
        
    @staticmethod  
    async def get_building_rooms_mapping(uow: AbstractUnitOfWork) -> dict[str, dict[str, int]]:
        async with uow:
            buildings = await uow.buildings_repo.get_all_joined_rooms()
            building_rooms_mapping = {}
            for b in buildings:
                rooms_mapping = {}

                if b.rooms is None: 
                    continue

                for r in b.rooms:
                    rooms_mapping[r.title] = r.id

                building_rooms_mapping[b.title] = rooms_mapping

        return building_rooms_mapping 

    @staticmethod
    async def prepare_building_sturcture_for_cache(uow: AbstractUnitOfWork) -> BuildingsForCache:
        async with uow:
            buildings = await uow.buildings_repo.get_all_joined_rooms()
            building_rooms_mapping = {}

            for b in buildings:
                rooms_mapping = {}

                if b.rooms != None:
                    for r in b.rooms:
                        short_title = r.title.split(" ")[0]
                        rooms_mapping[short_title] = r.external_id

                building_rooms_mapping[b.title] = BuildingForCache(
                    rooms=rooms_mapping,
                    id=b.external_id
                )

        return building_rooms_mapping

    @staticmethod
    async def serialize_buildings_for_cache(data: BuildingsForCache) -> str:
        return dumps({k: v.model_dump() for k, v in data.items()}, indent=1)
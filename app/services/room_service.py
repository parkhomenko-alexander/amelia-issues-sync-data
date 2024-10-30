import os
from typing import Any

import pandas as pd
from loguru import logger

from app.db.models.building import Building
from app.db.models.company import Company
from app.db.models.floor import Floor
from app.db.models.room import Room
from app.db.models.tech_passport import TechPassport
from app.schemas.room_schemas import RoomPostSchema
from app.services.services_helper import with_uow
from app.utils.unit_of_work import AbstractUnitOfWork


class RoomService():
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    @with_uow
    async def bulk_insert(self, elements_post: list[RoomPostSchema]) -> int:
        """
        Rooms inserting
        """
        elements_data_for_inserting = [e.model_dump() for e in elements_post]
        try:
            await self.uow.room_repo.bulk_insert(elements_data_for_inserting)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Rooms between {elements_post[0].external_id}-{elements_post[-1].external_id} were inserted")
        return 0

    @with_uow
    async def bulk_update(self, elements_update: list[RoomPostSchema]) -> int:
        """
        Rooms updating
        """
        elements_data_for_updating = [e.model_dump() for e in elements_update]
        try:
            await self.uow.room_repo.bulk_update_by_external_ids(elements_data_for_updating)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Rooms between {elements_update[0].external_id}-{elements_update[-1].external_id} were updated")
        return 0                 
    
    @with_uow
    async def bulk_delete(self, elements_delete: list[int]) -> int:
        """
        Rooms deleting
        """
        try:
            await self.uow.room_repo.bulk_delete(elements_delete)
            await self.uow.commit()
        except Exception as e:
            logger.error(f"Some error occurred: {e}")
            return 1
        
        logger.info(f"Rooms were deleted")
        return 0           

    @with_uow
    async def get_existing_external_ids(self, ids: list[int]) -> set[int]:
        return await self.uow.room_repo.get_existing_external_ids(ids)

    @with_uow
    async def generate_general_rooms_report(self) -> str:
            columns = [
                "ID здания", "Навание здания", "ID уровня", 
                "Навание уровня", "ID помещения", "Название помещения",
                "№ помещения", "Организация", "Площадь помещения", "Этаж", "Название помещения (если есть)",
                "Краткое описание помещения", "Текущий статус", "Вид объекта", "Класс объекта",
                "Тип объекта", "Институт/Школа/Проректор",	"Наименование структурного подразделения",
                "Ответственный сотрудник", "Приказ/Распоряжение о закреплении", "Учебный процесс",	"Научная деятельность",
                "Конгрессно-выставочное", "Спортивно-оздоровительная деятельность",	"Производственная деятельность",
                "Социально-общественное", "ID внешней системы",	"Количество рабочих мест для сотрудников (всего)",
                "Количество рабочих мест сотрудников (АРМ)", "Текущее состояние объекта", "Наличие окон/естественного освещения",
                "Тип искусственного освещения", "Тип светозащитной конструкции", "Количество учебных мест (всего)",	"Количество учебных мест (АРМ)", 
                "Компьютерный класс", "Поточная аудитория", "Водоснабжение", "Канализация (водоотведение, туалет)","Наличие подключений 220 V",
                "Наличие подключений 380 V", "Ethernet", "Старое название", "План помещения", "№ помещения"
            ]

            res = await self.uow.room_repo.get_roooms_floors_building_techpassport()
        
            lst = []
            for row in res:
                room: Room = row[0]
                floor: Floor = row[1]
                building: Building = row[2]
                tech_passport: TechPassport = row[3]
                company: Company = row[4]
                company_2lvl: Company = row[5]

                
                new_row = {}
            
                new_row["ID здания"] = building.external_id
                new_row["Навание здания"]= building.title
                new_row["ID уровня"]= floor.title
                new_row["Навание уровня"]= floor.title
                new_row["ID помещения"]= room.external_id
                new_row["Название помещения"]= room.title
                new_row["№ помещения"]= room.title.split(" ")[0]
                new_row["Организация"]= company.full_name if company is not None else ""
                new_row["Площадь помещения"]= tech_passport.square if tech_passport is not None else ""
                new_row["Вид объекта"]= tech_passport.object_view if tech_passport is not None else ""
                new_row["Класс объекта"]= tech_passport.object_class if tech_passport is not None else ""
                new_row["Тип объекта"]= tech_passport.object_type if tech_passport is not None else ""
                new_row["Институт/Школа/Проректор"]= company_2lvl.full_name if company_2lvl is not None else "" 	
                new_row["Наименование структурного подразделения"]= tech_passport.organization_3lvl if tech_passport is not None else ""
                new_row["Количество учебных мест (всего)"]= tech_passport.number_study_places if tech_passport is not None else ""

                lst.append(new_row)

            df = pd.DataFrame(lst, columns=columns)

            ROOT_DIR = os.getcwd()
            file_path = ROOT_DIR + '/reports/rooms_general_report.xlsx'

            df.to_excel(file_path, index=False, engine='openpyxl')

            return file_path

    @staticmethod
    async def rooms_ids(uow: AbstractUnitOfWork, building_ids: list[int] | None = None, facility_id: int = 0) -> list[int]:
        async with uow:
            ids: list[int] = []
            if building_ids:
                filters = [uow.room_repo.model.building_id == b_id for b_id in building_ids]
                rooms = await uow.room_repo.get_all_fitered_or(filters)
            else:
                rooms = await uow.room_repo.get_all_by_facility(facility_id)
            for r in rooms:
                ids.append(r.external_id)
        return ids

    @staticmethod
    async def get_title_external_id_mapping(uow: AbstractUnitOfWork) -> dict[str, int]:
        async with uow:
            rooms = await uow.room_repo.get_all()
            rooms_title_id_mapped: dict[str, int] = {}
            for r in rooms:
                rooms_title_id_mapped[r.title] = r.external_id
            return rooms_title_id_mapped

    @staticmethod
    async def get_external_id_title_mapping(uow: AbstractUnitOfWork) -> dict[int, str]:
        async with uow:
            rooms = await uow.room_repo.get_all()
            rooms_title_id_mapped: dict[int, str] = {}
            for r in rooms:
                rooms_title_id_mapped[r.external_id] = r.title.split(" ")[0]
            return rooms_title_id_mapped

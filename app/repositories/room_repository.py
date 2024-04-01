from typing import Sequence
from sqlalchemy import Result, Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.company import Company
from app.db.models.floor import Floor
from app.db.models.room import Room
from app.db.models.building import Building
from app.db.models.tech_passport import TechPassport
from app.repositories.abstract_repository import SQLAlchemyRepository


class RoomRepository(SQLAlchemyRepository[Room]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Room)

    async def get_roooms_floors_building_techpassport(self) -> Sequence[Row[tuple[Room, Floor, Building, TechPassport]]]:
        stmt = (
            select(
                self.model,
                Floor,
                Building,
                TechPassport,
                Company
            )
            .join(
                Floor,
                self.model.floor_id == Floor.id
            )
            .join(
                Building,
                Floor.building_id == Building.id 
            )
            .join(
                TechPassport,
                self.model.external_id == TechPassport.external_id
            )
            .outerjoin(
                Company,
                TechPassport.company_id==Company.id
            )
        )

        res: Result = await self.async_session.execute(stmt)
        all_rows: Sequence[Row[tuple[Room, Floor, Building, TechPassport]]] = res.all() 

        return all_rows
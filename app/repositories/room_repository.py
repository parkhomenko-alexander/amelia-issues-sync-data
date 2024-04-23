from typing import Sequence
from sqlalchemy import Result, Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.company import Company
from app.db.models.floor import Floor
from app.db.models.room import Room
from app.db.models.building import Building
from app.db.models.tech_passport import TechPassport
from app.repositories.abstract_repository import SQLAlchemyRepository

from sqlalchemy.orm import aliased


class RoomRepository(SQLAlchemyRepository[Room]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Room)

    async def get_roooms_floors_building_techpassport(self) -> Sequence[Row[tuple[Room, Floor, Building, TechPassport, Company, Company]]]:
        CopmanyAlias1 = aliased(Company)
        CopmanyAlias2 = aliased(Company)
        stmt = (
            select(
                self.model,
                Floor,
                Building,
                TechPassport,
                CopmanyAlias1,
                CopmanyAlias2
            )
            .join(
                Floor,
                self.model.floor_id==Floor.id
            )
            .join(
                Building,
                Floor.building_id==Building.id 
            )
            .outerjoin(
                TechPassport,
                self.model.external_id==TechPassport.external_id
            )
            .outerjoin(
                CopmanyAlias1,
                TechPassport.company_id==CopmanyAlias1.external_id
            )
            .outerjoin(
                CopmanyAlias2,
                TechPassport.organization_2lvl==CopmanyAlias2.external_id
            )
        )

        res: Result = await self.async_session.execute(stmt)
        all_rows = res.all() 

        return all_rows
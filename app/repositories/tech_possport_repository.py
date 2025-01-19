from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.tech_passport import TechPassport

from app.repositories.abstract_repository import SQLAlchemyRepository


class TechPassportRepository(SQLAlchemyRepository[TechPassport]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, TechPassport)
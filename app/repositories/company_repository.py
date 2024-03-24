from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.company import Company 
from app.repositories.abstract_repository import SQLAlchemyRepository


class CompanyRepository(SQLAlchemyRepository[Company]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Company)
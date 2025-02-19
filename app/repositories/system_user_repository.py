from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.system_user import SystemUser
from app.repositories.abstract_repository import SQLAlchemyBaseRepository, SQLAlchemyRepository


class SystemUserRepository(SQLAlchemyBaseRepository[SystemUser]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, SystemUser)
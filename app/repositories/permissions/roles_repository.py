from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.role import Role
from app.repositories.abstract_repository import SQLAlchemyBaseRepository


class RoleRepository(SQLAlchemyBaseRepository[Role]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Role)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.permission import Permission
from app.repositories.abstract_repository import SQLAlchemyBaseRepository


class PermissionRepository(SQLAlchemyBaseRepository[Permission]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Permission)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.role import Role
from app.db.models.role_permission import RolePermission
from app.repositories.abstract_repository import SQLAlchemyBaseRepository


class RolePermissionRepository(SQLAlchemyBaseRepository[RolePermission]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, RolePermission)
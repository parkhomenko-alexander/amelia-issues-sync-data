from sqlalchemy import Subquery, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.issue import Issue
from app.db.models.status_history import StatusHistory
from app.repositories.abstract_repository import SQLAlchemyRepository


class IssueRepository(SQLAlchemyRepository[Issue]):
    def __init__(self, async_session: AsyncSession):
        super().__init__(async_session, Issue)


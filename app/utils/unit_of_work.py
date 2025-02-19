from abc import ABC, abstractmethod

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db
from app.repositories import (BuildingRepository, CompanyRepository,
                              FacilityRepository, FloorRepository,
                              IssueRepository, PriorityRepository,
                              RoomRepository, ServiceRepository,
                              StatusHistoryRepository, StatusRepository,
                              TechPassportRepository, UserRepository,
                              WorkCategoryRepository, WorkflowRepository)
from app.repositories.permissions.permission_repository import PermissionRepository
from app.repositories.permissions.role_permission_repository import RolePermissionRepository
from app.repositories.permissions.roles_repository import RoleRepository
from app.repositories.system_user_repository import SystemUserRepository


class AbstractUnitOfWork(ABC):
    service_repo: ServiceRepository
    buildings_repo: BuildingRepository
    company_repo: CompanyRepository
    facility_repo: FacilityRepository
    floor_repo: FloorRepository
    issues_repo: IssueRepository
    priority_repo: PriorityRepository
    room_repo: RoomRepository
    status_repo: StatusRepository
    statuses_history_repo: StatusHistoryRepository
    users_repo: UserRepository
    work_categories_repo: WorkCategoryRepository
    workflow_repo: WorkflowRepository
    tech_passport_repo: TechPassportRepository

    system_user_repo: SystemUserRepository
    role_repo: RoleRepository
    permission_repo: PermissionRepository
    role_permission_repo: RolePermissionRepository



    @abstractmethod
    def __init__(self, *args):
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args):
        await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    
    def __init__(self):
        self.async_session_factory = db.get_async_sessionmaker()

    async def __aenter__(self):
        self.async_session: AsyncSession = self.async_session_factory()

        self.service_repo = ServiceRepository(self.async_session)
        self.buildings_repo = BuildingRepository(self.async_session)
        self.company_repo = CompanyRepository(self.async_session)
        self.facility_repo = FacilityRepository(self.async_session)
        self.floor_repo = FloorRepository(self.async_session)
        self.issues_repo = IssueRepository(self.async_session)
        self.priority_repo = PriorityRepository(self.async_session)
        self.room_repo = RoomRepository(self.async_session)
        self.status_repo = StatusRepository(self.async_session)
        self.statuses_history_repo = StatusHistoryRepository(self.async_session)
        self.users_repo = UserRepository(self.async_session)
        self.work_categories_repo = WorkCategoryRepository(self.async_session)
        self.workflow_repo = WorkflowRepository(self.async_session)
        self.tech_passport_repo = TechPassportRepository(self.async_session)

        self.system_user_repo = SystemUserRepository(self.async_session)
        self.role_repo = RoleRepository(self.async_session)
        self.permission_repo = PermissionRepository(self.async_session)
        self.role_permission_repo = RolePermissionRepository(self.async_session)


    async def __aexit__(self, *args):
        await self.rollback()
        await self.async_session.close()
        
    async def commit(self):
        await self.async_session.commit()

    async def rollback(self):
        await self.async_session.rollback()
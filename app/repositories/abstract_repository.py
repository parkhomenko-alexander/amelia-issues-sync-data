from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy import insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count 
from app.db.base_model import Base


T = TypeVar('T', bound=Base)


class AbstractRepository(ABC, Generic[T]):

    @abstractmethod
    async def add_one(self, data: dict) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def get_all(self) -> Sequence[T]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_all_fitered_or(self, filter_by: list) -> Sequence[T]:
        raise NotImplementedError
    
    @abstractmethod
    async def find_one(self, **filter_by) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def bulk_update_by_external_ids(self, data: list[dict]):
        raise NotImplementedError
    
    @abstractmethod
    async def bulk_insert(self, data: list[dict]) -> int:
        raise NotImplementedError
    
    @abstractmethod
    async def get_count(self) -> int:
        raise NotImplementedError
    
    # @abstractmethod
    # async def get_id_from_external_ids(self, data: list[int]) -> list[int]:
    #     raise NotImplementedError
    

class SQLAlchemyRepository(AbstractRepository[T]):
    
    def __init__(self, async_session: AsyncSession, model: Type[T]):
        self.async_session = async_session
        self.model = model

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.async_session.execute(stmt)
        
        return res.scalar_one()

    async def get_all(self):
        stmt = select(self.model)
        res = await self.async_session.scalars(stmt)

        return res.all()
    
    async def get_all_fitered_or(self, filter_by: list):
        stmt = select(self.model).filter(
            or_(
                *filter_by
            )
        )

        res = await self.async_session.scalars(stmt)

        return res.all()


    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.async_session.execute(stmt)

        return res.scalar_one_or_none()

    async def edit_one(self, id: int, data: dict):
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        res = await self.async_session.execute(stmt)
        return res.scalar_one()

    async def bulk_update_by_external_ids(self, data: list[dict]) -> int:
        for item in data:
            stmt = (
                update(self.model).
                where(self.model.external_id == item["external_id"]).
                values(**item)
            )
        
            await self.async_session.execute(stmt)
         
        return 0
        
    async def bulk_insert(self, data: list[dict]) -> int:
        stmt = (
            insert(self.model),
            data
        )
        
        res = await self.async_session.execute(*stmt)
        return 0
    
    async def get_count(self) -> int:
        stmt = (
            count(self.model.id)
        )

        res = await self.async_session.execute(stmt)
        c = res.scalar_one()
        return c

    async def get_existing_external_ids(self, external_ids: list[int]) -> set[int]:
        stmt = (
            select(self.model.external_id).
            where(self.model.external_id.in_(external_ids))
        )

        res = await self.async_session.execute(stmt)

        return set(res.scalars().all())
    
    async def get_all_external_ids(self) -> Sequence[int]:
        stmt = (
            select(self.model.external_id)
        )
        res = await self.async_session.execute(stmt)
        return res.scalars().all()
    
    # async def bulk_insert_by_external_ids(self, data: list[dict]):
    #     for item in data:
    #         stmt = (
    #             update(self.model).
    #             where(self.model.external_id == item[""]).
    #             values(**item)
    #         )
        
    #         await self.async_session.execute(stmt)
         
    #     return 0
    #     return 0

    # async def get_id_from_external_ids(self, data: list[int]) -> list[int]:
    #     stmt = (
    #         select(self.model)
    #     )

    #     return [1]
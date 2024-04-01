from typing import Annotated

from fastapi import Depends

from app.utils.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork


UowDep = Annotated[
    AbstractUnitOfWork, 
    Depends(SqlAlchemyUnitOfWork)
]
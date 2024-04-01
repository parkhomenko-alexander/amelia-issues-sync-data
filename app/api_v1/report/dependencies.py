from typing import Annotated

from fastapi import Depends


# RoomServiceDep = Annotated[
#     AbstractUnitOfWork, 
#     Depends(SqlAlchemyUnitOfWork)
# ]
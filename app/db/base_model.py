from datetime import datetime, tzinfo
from typing import TypeVar
from typing_extensions import Annotated
from pytz import timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry


str_350 = Annotated[str, mapped_column(String(350))]

class Base(DeclarativeBase):
    __abstract__ = True

    registry = registry(
        type_annotation_map={
            str_350: String(350),
        }
    )


    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_id: Mapped[int] = mapped_column(unique=True)


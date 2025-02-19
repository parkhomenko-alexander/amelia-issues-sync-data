from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base_model import Base, BaseMixinAmelia, str_350

if TYPE_CHECKING:
    ...

class TechPassport(Base, BaseMixinAmelia):
    __tablename__ = "tech_passports"

    title: Mapped[str_350]
    object_view: Mapped[str_350 | None]
    object_type:  Mapped[str_350 | None]
    object_class:  Mapped[str_350 | None]
    organization_3lvl: Mapped[str_350 | None]
    square: Mapped[float | None]
    number_study_places: Mapped[float | None]

    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.external_id")) 
    floor_id: Mapped[int | None] = mapped_column(ForeignKey("floors.external_id"))
    organization_2lvl: Mapped[int | None] = mapped_column(ForeignKey("companies.external_id")) 


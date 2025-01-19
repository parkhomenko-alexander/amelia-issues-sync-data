from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.room import Room
    from app.db.models.building import Building
    from app.db.models.facility import Facility


class Floor(Base):
    __tablename__ = "floors"

    title: Mapped[str_350]
    
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    
    building: Mapped["Building"] = relationship(back_populates="floors", uselist=False)
    rooms: Mapped["Room"] = relationship(back_populates="floor", uselist=True)
    facility: Mapped["Facility"] = relationship(back_populates="floors", uselist=False, foreign_keys=facility_id)

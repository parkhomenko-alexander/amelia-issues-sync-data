from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.issue import Issue
    from app.db.models.service import Service
    from app.db.models.floor import Floor
    from app.db.models.room import Room
    from app.db.models.facility import Facility


class Building(Base):
    __tablename__ = "buildings"

    title: Mapped[str_350]
    address: Mapped[str_350 | None]
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    

    floors: Mapped[list["Floor"] | None] = relationship(back_populates="building", uselist=True)
    rooms: Mapped[list["Room"] | None] = relationship(back_populates="building", uselist=True)
    issues: Mapped[list["Issue"] | None] = relationship(back_populates="building", uselist=True)
    facility: Mapped["Facility"] = relationship(back_populates="buildings", uselist=False, foreign_keys=[facility_id])

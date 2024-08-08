from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.building import Building
    from app.db.models.floor import Floor
    from app.db.models.issue import Issue

    # from app.db.models.room_tech_passports import RoomTechPassports



class Room(Base):
    __tablename__ = "rooms"

    title: Mapped[str_350]
    

    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"))
    facility_id: Mapped[int] =  mapped_column(ForeignKey("facilities.id"))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"))

    floor: Mapped["Floor"] = relationship(back_populates="rooms", uselist=False, foreign_keys=[floor_id])
    building: Mapped["Building"] = relationship(back_populates="rooms", uselist=False, foreign_keys=[building_id])
    issues: Mapped["Issue"] = relationship(back_populates="room", uselist=True)
    # tech_passports: Mapped[list["RoomTechPassports"] | None] = relationship(back_populates="room", uselist=True)


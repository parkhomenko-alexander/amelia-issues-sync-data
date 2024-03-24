from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.room import Room
    from app.db.models.company import Company



class RoomTechPassports(Base):
    __tablename__ = "rooms_tech_passports"

    object_view: Mapped[Optional[str_350]]
    object_class: Mapped[Optional[str_350]]
    object_type: Mapped[Optional[str_350]]
    structural_unit: Mapped[Optional[str_350]]
    square: Mapped[Optional[float]]
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))

    institute_school_provost_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"))

    company: Mapped[Optional["Company"]] = relationship(back_populates="tech_passports", uselist=False)
    room: Mapped["Room"] = relationship(back_populates="tech_passports", uselist=False)
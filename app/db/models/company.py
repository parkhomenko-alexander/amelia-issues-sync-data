from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, BaseMixinAmelia, str_350

if TYPE_CHECKING:
    # from app.db.models.room_tech_passports import RoomTechPassports
    from app.db.models.facility import Facility
    from app.db.models.issue import Issue
    from app.db.models.user import User




class Company(Base, BaseMixinAmelia):
    __tablename__ = "companies"

    full_name: Mapped[str_350]
    
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))

    facility: Mapped["Facility"] = relationship(back_populates="companies", uselist=False, foreign_keys=[facility_id])
    issues: Mapped[Optional[list["Issue"]]] = relationship(back_populates="company", uselist=True)
    users: Mapped["User"] = relationship(back_populates="company", uselist=True)
    # tech_passports: Mapped[Optional["RoomTechPassports"]] = relationship(back_populates="company", uselist=True)


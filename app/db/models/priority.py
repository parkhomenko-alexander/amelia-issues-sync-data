from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.facility import Facility
    from app.db.models.issue import Issue
    
class Priority(Base):
    __tablename__ = "priorities"

    title: Mapped[str_350]
    weight: Mapped[int | None]
    
    facility_id: Mapped[int | None] = mapped_column(ForeignKey("facilities.id"))

    ficility: Mapped["Facility"] =  relationship(back_populates="priorities", uselist=False)
    issues: Mapped[Optional[list["Issue"]]] = relationship(back_populates="priority", uselist=True)
    
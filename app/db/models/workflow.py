from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.status import Status
    from app.db.models.facility import Facility
    from app.db.models.issue import Issue



class Workflow(Base):
    __tablename__ = "workflows"

    title: Mapped[str_350]
    
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id")) 

    facility: Mapped[Optional["Facility"]] =  relationship(back_populates="workflow", uselist=False, foreign_keys=[facility_id])
    issues: Mapped[Optional["Issue"]] =  relationship(back_populates="workflow", uselist=True)
    statuses: Mapped["Status"] = relationship(back_populates="workflow", uselist=True)

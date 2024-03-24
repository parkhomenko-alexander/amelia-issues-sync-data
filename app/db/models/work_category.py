from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.status_history import StatusHistory
    from app.db.models.issue import Issue
    from app.db.models.service import Service
    from app.db.models.facility import Facility

    
class WorkCategory(Base):
    __tablename__ = "work_categories"

    title: Mapped[str_350]
    

    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))

    service: Mapped[Optional["Service"]] =  relationship(back_populates="work_categories", uselist=False)
    issues: Mapped[Optional[list["Issue"]]] = relationship(back_populates="work_category", uselist=True)
    facility: Mapped[Optional["Facility"]] = relationship(back_populates="work_categories", uselist=False)
    
    # statuses_history: Mapped["StatusHistory"] = relationship(back_populates="work_category", uselist=True)

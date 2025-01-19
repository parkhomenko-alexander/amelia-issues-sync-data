from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.status_history import StatusHistory
    from .work_category import WorkCategory
    from app.db.models.issue import Issue
    from app.db.models.issue import Facility


class Service(Base):
    __tablename__ = "services"

    title: Mapped[str_350]
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))   

    facility: Mapped["Facility"] = relationship(back_populates="services", uselist=False, foreign_keys=[facility_id])
    work_categories: Mapped[Optional[list["WorkCategory"]]] = relationship(back_populates="service", uselist=True)
    issues: Mapped[Optional[list["Issue"]]] = relationship(back_populates="service", uselist=True)

    # statuses_history: Mapped["StatusHistory"] = relationship(back_populates="service", uselist=True)
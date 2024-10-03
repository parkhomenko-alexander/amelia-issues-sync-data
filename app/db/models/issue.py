from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.building import Building
    from app.db.models.company import Company
    from app.db.models.facility import Facility
    from app.db.models.priority import Priority
    from app.db.models.room import Room
    from app.db.models.service import Service
    from app.db.models.status_history import StatusHistory
    from app.db.models.user import User
    from app.db.models.work_category import WorkCategory
    from app.db.models.workflow import Workflow



class Issue(Base):
    __tablename__ = "issues"

    description: Mapped[str]
    finish_date_plane: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dead_line: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rating: Mapped[int | None]
    tel: Mapped[str_350 | None]
    email: Mapped[str_350 | None]
    work_place: Mapped[str | None]

    work_category_id: Mapped[int] = mapped_column(ForeignKey("work_categories.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.external_id"))
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"))
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id")) 
    priority_id: Mapped[int | None] = mapped_column(ForeignKey("priorities.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    declarer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id")) 
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id", ondelete="SET NULL"))
    # facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))

    work_category: Mapped["WorkCategory"] = relationship(back_populates="issues", uselist=False, foreign_keys=[work_category_id])
    service: Mapped["Service"] = relationship(back_populates="issues", uselist=False, foreign_keys=[service_id])
    workflow: Mapped["Workflow"] = relationship(back_populates="issues", uselist=False, foreign_keys=[workflow_id])
    priority: Mapped["Priority"] = relationship(back_populates="issues", uselist=False, foreign_keys=[priority_id])
    company: Mapped["Company"] = relationship(back_populates="issues", uselist=False, foreign_keys=[company_id])
    # creator: Mapped["User"] = relationship(back_populates="issues_creator", uselist=False, foreign_keys=[user_id])
    declarer: Mapped["User"] = relationship(back_populates="issues_declarer", uselist=False, foreign_keys=[declarer_id])
    executor: Mapped["User"] = relationship(back_populates="issues_executor", uselist=False, foreign_keys=[executor_id])
    statuses_history: Mapped["StatusHistory"] = relationship(
        back_populates="issue", 
        uselist=True,
        cascade ="all, delete-orphan",
        passive_deletes=True
    )
    building: Mapped["Building"] = relationship(back_populates="issues", uselist=False, foreign_keys=[building_id])
    room: Mapped["Room"] = relationship(back_populates="issues", uselist=False, foreign_keys=[room_id])
    # facility: Mapped["Facility"] = relationship(back_populates="issues", uselist=False, foreign_keys=[facility_id])


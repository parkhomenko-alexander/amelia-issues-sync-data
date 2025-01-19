from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.status_history import StatusHistory
    from app.db.models.workflow import Workflow
    from app.db.models.facility import Facility
    from app.db.models.issue import Issue
    from app.db.models.user import User




class Status(Base):
    __tablename__ = "statuses"

    title: Mapped[str_350]
    is_accepted: Mapped[bool]
    is_terminated: Mapped[bool]
    is_started: Mapped[bool]
    percentage_completion: Mapped[int | None]
    

    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"))

    workflow: Mapped["Workflow"] = relationship(back_populates="statuses", uselist=False)
    # statuses_history: Mapped["StatusHistory"] = relationship(back_populates="status", uselist=True)
    
    
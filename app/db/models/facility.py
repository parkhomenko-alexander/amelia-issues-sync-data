from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.priority import Priority
    from app.db.models.issue import Issue
    from app.db.models.workflow import Workflow
    from app.db.models.user import User
    from app.db.models.company import Company
    from app.db.models.issue import Service
    from app.db.models.work_category import WorkCategory
    from app.db.models.building import Building
    from app.db.models.floor import Floor





    
class Facility(Base):
    __tablename__ = "facilities"

    title: Mapped[str_350]
    

    workflow: Mapped[Optional["Workflow"]] =  relationship(back_populates="facility", uselist=False)
    # issues: Mapped[Optional[list["Issue"]]] = relationship(back_populates="facility", uselist=True)
    priorities: Mapped["Priority"] =  relationship(back_populates="ficility", uselist=True)
    companies: Mapped["Company"] = relationship(back_populates="facility", uselist=True)
    users: Mapped["User"] = relationship(back_populates="facility", uselist=True)
    services : Mapped[list["Service"]] = relationship(back_populates="facility", uselist=True)
    work_categories: Mapped[Optional[list["WorkCategory"]]] = relationship(back_populates="facility", uselist=True)
    buildings: Mapped[Optional[list["Building"]]] = relationship(back_populates="facility", uselist=False)
    floors: Mapped[Optional[list["Floor"]]] = relationship(back_populates="facility", uselist=True)
    
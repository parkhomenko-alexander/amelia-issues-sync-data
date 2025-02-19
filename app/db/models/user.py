from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, BaseMixinAmelia, str_350

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.facility import Facility
    from app.db.models.issue import Issue
    from app.db.models.status_history import StatusHistory



class User(Base, BaseMixinAmelia):
    __tablename__ = "users"

    first_name: Mapped[str_350 | None]
    last_name: Mapped[str_350 | None]
    middle_name: Mapped[Optional[str_350]]
    email: Mapped[str_350]
    notification_email: Mapped[Optional[str_350]]
    tel: Mapped[Optional[str_350]]
    role: Mapped[str_350]
    working: Mapped[bool]
    # additional_services_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer)) 
    # additional_service: Mapped[Optional[int]] = mapped_column(ForeignKey("services.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))


    company: Mapped["Company"] = relationship(back_populates="users", uselist=False, foreign_keys=[company_id])
    facility: Mapped["Facility"] = relationship(back_populates="users", uselist=False, foreign_keys=[facility_id])
    
    # issues_creator: Mapped[Optional[list["Issue"]]] = relationship(
    #     back_populates="creator", uselist=True,
    #     primaryjoin="User.id==Issue.user_id"
    # )
    issues_declarer: Mapped[Optional[list["Issue"]]] = relationship(
        back_populates="declarer", uselist=True,
        primaryjoin="User.id==Issue.declarer_id"
    )
    issues_executor: Mapped[Optional[list["Issue"]]] = relationship(
        back_populates="executor", uselist=True,
        primaryjoin="User.id==Issue.executor_id"
    )
    # statuses_history: Mapped["StatusHistory"] = relationship(back_populates="user", uselist=True)


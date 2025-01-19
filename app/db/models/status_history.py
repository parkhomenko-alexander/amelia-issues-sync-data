from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350
from app.db.models.user import User

if TYPE_CHECKING:
    from app.db.models.work_category import WorkCategory
    from app.db.models.service import Service
    from app.db.models.status import Status
    from app.db.models.issue import Issue



class StatusHistory(Base):
    __tablename__ = "statuses_history"

    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.external_id", ondelete="CASCADE"))
    message: Mapped[str]
    percentage: Mapped[int]
    status: Mapped[str_350]
    user: Mapped[str_350]

    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"))
    # service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    # work_category_id: Mapped[int] = mapped_column(ForeignKey("work_categories.id"))

    issue: Mapped["Issue"] = relationship(back_populates="statuses_history", uselist=False, foreign_keys=[issue_id])
    # user: Mapped["User"] = relationship(back_populates="statuses_history", uselist=False, foreign_keys=[user_id])
    # status: Mapped["Status"] = relationship(back_populates="statuses_history", uselist=False, foreign_keys=[status_id])
    # service: Mapped["Service"] = relationship(back_populates="statuses_history", uselist=False, foreign_keys=[service_id])
    # work_category: Mapped["WorkCategory"] = relationship(back_populates="statuses_history", uselist=False, foreign_keys=[work_category_id])
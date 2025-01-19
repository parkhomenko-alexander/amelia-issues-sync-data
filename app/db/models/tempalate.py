from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import Base, str_350

if TYPE_CHECKING:
    from app.db.models.issue import Issue
    from .service import Service
    
class Template(Base):
    __tablename__ = "..."

    title: Mapped[str_350]
    

    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"))

    service: Mapped[Optional["Service"]] =  relationship(back_populates="work_categories", uselist=False)
    issues: Mapped[Optional[list["Issue"]]] = relationship(back_populates="work_category", uselist=True)

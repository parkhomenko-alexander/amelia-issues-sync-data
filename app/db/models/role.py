from app.db.base_model import Base, BaseMixin

from sqlalchemy.orm import Mapped, mapped_column

class Role(Base, BaseMixin):
    __tablename__ = "roles"

    title: Mapped[str] = mapped_column(unique=True)
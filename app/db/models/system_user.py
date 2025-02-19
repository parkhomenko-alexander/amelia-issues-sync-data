from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


from app.db.base_model import Base, BaseMixin


class SystemUser(Base, BaseMixin):
    __tablename__ = "system_users"

    login: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    timezone: Mapped[str]

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
from app.db.base_model import Base, BaseMixin

from sqlalchemy.orm import Mapped

class Permission(Base, BaseMixin):
    __tablename__ = "permissions"

    title: Mapped[str]
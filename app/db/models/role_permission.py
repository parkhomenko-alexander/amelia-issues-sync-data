from sqlalchemy import ForeignKey
from app.db.base_model import Base, BaseMixin

from sqlalchemy.orm import Mapped, mapped_column

class RolePermission(Base, BaseMixin):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"))
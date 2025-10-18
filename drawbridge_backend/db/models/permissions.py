from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from drawbridge_backend.db.base import Base


class NameSpacePermissionModel(Base):

    __tablename__ = "namespace_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    namespace_id: Mapped[int] = mapped_column(
        ForeignKey("namespaces.id"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    can_edit: Mapped[bool] = mapped_column(nullable=False, default=False)


class TablePermissionModel(Base):
    """
    Права доступа на изменение строк
    """

    __tablename__ = "table_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    is_edit_disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_read_disabled: Mapped[bool] = mapped_column(nullable=False, default=False)


class FieldPermissionModel(Base):
    """
    Права доступа на изменение колонок
    """

    __tablename__ = "field_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    is_edit_disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_read_disabled: Mapped[bool] = mapped_column(nullable=False, default=False)

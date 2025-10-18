from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from drawbridge_backend.db.base import Base
from drawbridge_backend.domain.enums import DataTypeEnum


class NameSpaceModel(Base):
    """Base class for all namespace models."""

    __tablename__ = "namespaces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    description: Mapped[str | None]

    tables: Mapped[list["TableModel"]] = relationship(
        back_populates="namespace",
    )


class TableModel(Base):
    """Base class for all table models."""

    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None]
    namespace_id: Mapped[int] = mapped_column(
        ForeignKey("namespaces.id"),
        nullable=True,
    )

    fields: Mapped[list["FieldModel"]] = relationship(
        back_populates="table",
        cascade="all, delete-orphan",
    )
    namespace: Mapped["NameSpaceModel"] = relationship(back_populates="tables")


class FieldModel(Base):
    """Base class for all field models."""

    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(256), nullable=False)
    data_type: Mapped[DataTypeEnum] = mapped_column(
        Enum(DataTypeEnum, native_enum=False),
        nullable=False,
    )

    is_nullable: Mapped[bool] = mapped_column(nullable=False, default=True)
    default_value: Mapped[str | None] = mapped_column(String(256), nullable=True)
    table: Mapped["TableModel"] = relationship(back_populates="fields")

    choices: Mapped[list["FieldChoiceModel"]] = relationship(
        back_populates="field",
        cascade="all, delete-orphan",
    )


class FieldChoiceModel(Base):
    """
    Base class for all field choices models.
    """

    __tablename__ = "field_choices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"), nullable=False)
    value: Mapped[str] = mapped_column(String(256), nullable=False)

    field: Mapped["FieldModel"] = relationship(back_populates="choices")

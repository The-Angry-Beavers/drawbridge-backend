from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, relationship, mapped_column

from drawbridge_backend.db.base import Base
from drawbridge_backend.domain.enums import DataTypeEnum


class TableModel(Base):
    """Base class for all table models."""

    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None]

    fields: Mapped[list["FieldModel"]] = relationship(
        back_populates="table", cascade="all, delete-orphan"
    )


class FieldModel(Base):
    """Base class for all field models."""

    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    verbose_name: Mapped[str] = mapped_column(String(256), nullable=False)
    data_type: Mapped[DataTypeEnum] = mapped_column(
        Enum(DataTypeEnum, native_enum=False), nullable=False
    )

    is_nullable: Mapped[bool] = mapped_column(nullable=False, default=True)
    default_value: Mapped[str | None] = mapped_column(String(256), nullable=True)
    table: Mapped["TableModel"] = relationship(back_populates="fields")

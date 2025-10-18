import datetime

from pydantic import BaseModel, Field

from drawbridge_backend.domain.enums import DataTypeEnum
from drawbridge_backend.domain.tables.entities import (
    FilteringParam,
    OrderingParam,
    RowData,
)


class ChoiceSchema(BaseModel):
    id: int = Field(alias="choice_id")
    value: str


class FieldSchema(BaseModel):
    id: int = Field(alias="field_id")
    name: str
    verbose_name: str
    data_type: DataTypeEnum
    is_nullable: bool
    default_value: str | None
    choices: list[ChoiceSchema] | None = None


class UpdateFieldDataSchema(BaseModel):
    name: str | None
    verbose_name: str | None
    is_nullable: bool | None
    default_value: str | None
    choices: list[str] | None = None


class UpdateFieldSchema(BaseModel):
    table_id: int
    field_id: int
    updated_data: UpdateFieldDataSchema


class AddFieldSchema(BaseModel):
    table_id: int
    name: str
    verbose_name: str
    data_type: DataTypeEnum
    is_nullable: bool
    default_value: str | None
    choices: list[str] | None


class CreateFieldSchema(BaseModel):
    pass


class TableSchema(BaseModel):

    id: int = Field(alias="table_id")
    name: str
    verbose_name: str
    description: str | None
    namespace_id: int | None = None
    last_modified_at: datetime.datetime | None = None

    fields: list[FieldSchema]


class UpdateTableSchema(BaseModel):
    name: str
    verbose_name: str
    description: str | None
    namespace_id: int | None


class DeleteFieldSchema(BaseModel):
    table_id: int
    field_id: int


class NameSpaceSchema(BaseModel):

    id: int
    name: str
    description: str | None
    tables: list[TableSchema]


class _Val(BaseModel):
    value: str | int | float | bool | datetime.datetime | None


class ValueSchema(BaseModel):
    field_id: int
    type: DataTypeEnum = Field(alias="data_type")
    value: _Val


class RowSchema(BaseModel):
    id: int = Field(alias="row_id")
    values: list[ValueSchema]


class FetchRowsRequestSchema(BaseModel):
    table_id: int
    limit: int = 100
    offset: int = 0
    filter_params: list[FilteringParam] | None = None
    ordering_params: list[OrderingParam] | None = None


class FetchRowsResponseSchema(BaseModel):
    total: int
    rows: list[RowSchema]


class InsertRowSchema(BaseModel):
    values: list[RowData]  # type: ignore


class InsertRowsRequestSchema(BaseModel):
    table_id: int
    rows: list[InsertRowSchema]


class UpdateRowSchema(BaseModel):
    row_id: int
    new_values: list[RowData]  # type: ignore


class UpdateRowsRequestSchema(BaseModel):
    table_id: int
    updated_rows: list[UpdateRowSchema]


class InsertRowsResponseSchema(BaseModel):
    success: bool
    errors: list[str] | None


class DeleteRowsRequestSchema(BaseModel):
    table_id: int
    row_ids: list[int]

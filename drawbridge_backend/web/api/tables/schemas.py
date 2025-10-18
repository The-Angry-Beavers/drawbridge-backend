import datetime

from pydantic import BaseModel

from drawbridge_backend.domain.enums import DataTypeEnum
from drawbridge_backend.domain.tables.entities import FilteringParam, OrderingParam


class FieldSchema(BaseModel):
    id: int
    name: str
    verbose_name: str
    data_type: DataTypeEnum
    is_nullable: bool
    default_value: str | None
    choices: list[str] | None


class UpdateFieldDataSchema(BaseModel):
    name: str | None
    verbose_name: str | None
    is_nullable: bool | None
    default_value: str | None
    choices: list[str] | None


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

    id: int
    name: str
    verbose_name: str
    description: str | None
    namespace_id: int | None

    last_modified_at: datetime.datetime

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


class ValueSchema(BaseModel):
    field_id: int
    type: DataTypeEnum
    value: str | int | float | bool | datetime.datetime | None


class RowSchema(BaseModel):
    id: int
    values: list[ValueSchema]


class FetchRowsRequestSchema(BaseModel):
    limit: int = 100
    offset: int = 0
    filter_params: list[FilteringParam]
    ordering_params: list[OrderingParam]


class FetchRowsResponseSchema(BaseModel):
    total: int
    rows: RowSchema


class InsertRowSchema(BaseModel):
    values: list[ValueSchema]


class InsertRowsRequestSchema(BaseModel):
    table_id: int
    rows: list[InsertRowSchema]


class UpdateRowsRequestSchema(BaseModel):
    table_id: int
    updated_rows: list[InsertRowSchema]


class InsertRowsResponseSchema(BaseModel):
    success: bool
    errors: list[str] | None

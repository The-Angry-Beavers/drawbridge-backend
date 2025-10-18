from typing import Final, Type, Any

from sqlalchemy import MetaData, Table as SATable, Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.sql import sqltypes as sqlalchemy_types

from drawbridge_backend.domain.enums import DataTypeEnum
from drawbridge_backend.domain.tables.entities import (
    UpdateRow,
    Row,
    InsertRow,
    OrderingParam,
    FilteringParam,
    Table,
    UnSavedTable,
)
from drawbridge_backend.domain.tables.table_service import AbstractTableService

SQLALCHEMY_TYPES_MAP: Final[
    dict[DataTypeEnum, Type[sqlalchemy_types.TypeEngine[Any]]]
] = {
    DataTypeEnum.INT: sqlalchemy_types.Integer,
    DataTypeEnum.STRING: sqlalchemy_types.String,
    DataTypeEnum.BOOL: sqlalchemy_types.Boolean,
    DataTypeEnum.FLOAT: sqlalchemy_types.Float,
    DataTypeEnum.DATETIME: sqlalchemy_types.DateTime,
}


# def get_sa_table(table: Table, metadata: MetaData, engine: AsyncEngine) -> SATable:
#     columns = [Column("id", Integer, primary_key=True, autoincrement=True)]
#     for field in table.fields:
#         col_type = SQLALCHEMY_TYPES_MAP[field.data_type]
#         columns.append(
#             Column(
#                 field.name,
#                 col_type,
#                 nullable=field.is_nullable,
#                 default=field.default_value,
#             )
#         )
#
#     return SATable(table.name, metadata, *columns, autoload_with=engine)
#
#
# class SqlAlchemyTablesService(AbstractTableService):
#
#     def __init__(
#         self,
#         db_session: AsyncSession,
#         storage_db_session: AsyncSession,
#         storage_engine: AsyncEngine,
#     ) -> None:
#         self._db_session = db_session
#         self._storage_db_session = storage_db_session
#         self._metadata = MetaData()
#         self._storage_engine = storage_engine
#
#     async def fetch_rows(
#         self,
#         table: Table,
#         limit: int = 100,
#         offset: int = 0,
#         ordering_params: list[OrderingParam] | None = None,
#         filtering_params: list[FilteringParam] | None = None,
#     ) -> list[Row]:
#         pass
#
#     async def insert_rows(self, rows: list[InsertRow]) -> list[Row]:
#         pass
#
#     async def update_rows(self, rows: list[UpdateRow]) -> list[Row]:
#         pass
#
#     async def delete_rows(self, table: Table, row_ids: list[int]) -> None:
#         pass
#
#     async def update_table(self, table: Table) -> Table:
#         pass
#
#     async def create_table(self, table: UnSavedTable) -> Table:
#         pass
#
#     async def get_table_by_id(self, table_id: int) -> Table | None:
#         pass

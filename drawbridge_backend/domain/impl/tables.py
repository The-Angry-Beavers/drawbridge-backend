from typing import Any, Final, Type, cast

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    Select,
    delete,
    func,
    select,
    update,
    Table as SATable,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import sqltypes as sqlalchemy_types
from typing_extensions import TypeVar

from drawbridge_backend.db.models.tables import FieldModel, TableModel, FieldChoiceModel
from drawbridge_backend.domain.enums import DataTypeEnum
from drawbridge_backend.domain.tables.entities import (
    BaseValue,
    BoolValue,
    DateTimeValue,
    Field,
    FilteringParam,
    FloatValue,
    InsertRow,
    IntValue,
    OrderingParam,
    Row,
    RowData,
    StringValue,
    Table,
    UnSavedTable,
    UpdateRow,
    ChoiceValue,
    FieldChoice,
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
    DataTypeEnum.CHOICE: sqlalchemy_types.Integer,
}


def get_sa_table(table: Table, metadata: MetaData) -> SATable:
    columns = [Column("id", Integer, primary_key=True, autoincrement=True)]
    for field in table.fields:
        col_type = SQLALCHEMY_TYPES_MAP[field.data_type]
        columns.append(
            Column(
                field.name,
                col_type,
                nullable=field.is_nullable,
                default=field.default_value,
            ),
        )

    return SATable(
        table.name,
        metadata,
        *columns,
        extend_existing=True,
    )


def map_to_rows(table: Table, dict_rows: list[dict[str, Any]]) -> list[Row]:
    rows: list[Row] = []
    for d in dict_rows:
        values: list[RowData[BaseValue]] = []
        for field in table.fields:
            raw_value = d.get(field.name)
            if raw_value is None:
                val: BaseValue = BaseValue(None)
            elif field.data_type == DataTypeEnum.INT:
                val = IntValue(raw_value)
            elif field.data_type == DataTypeEnum.STRING:
                val = StringValue(raw_value)
            elif field.data_type == DataTypeEnum.BOOL:
                val = BoolValue(raw_value)
            elif field.data_type == DataTypeEnum.FLOAT:
                val = FloatValue(raw_value)
            elif field.data_type == DataTypeEnum.CHOICE:
                val = ChoiceValue(raw_value)
            elif field.data_type == DataTypeEnum.DATETIME:
                val = DateTimeValue(raw_value)
            else:
                val = BaseValue(raw_value)
            values.append(RowData(field_id=field.field_id, value=val))
        rows.append(Row(table=table, row_id=d["id"], values=values))
    return rows


T = TypeVar("T", bound=Any)


def _add_ordering_params_to_stmt(
    stmt: Select[T],
    ordering_params: list[OrderingParam],
) -> Select[T]:
    # TODO: Implement
    return stmt


def _add_filtering_params_to_stmt(
    stmt: Select[T],
    filtering_params: list[FilteringParam],
) -> Select[T]:
    # TODO: Implement
    return stmt


def map_table_model_to_domain(table_model: TableModel) -> Table:
    """Преобразует TableModel в доменную модель Table."""
    fields = [
        Field(
            _field_id=f.id,
            name=f.name,
            verbose_name=f.verbose_name,
            data_type=f.data_type,
            is_nullable=f.is_nullable,
            default_value=f.default_value,
            choices=[FieldChoice(_choice_id=c.id, value=c.value) for c in f.choices],
        )
        for f in table_model.fields
    ]

    return Table(
        table_id=table_model.id,
        name=table_model.name,
        fields=fields,
        verbose_name=table_model.verbose_name,
        description=table_model.description,
    )


class SqlAlchemyTablesService(AbstractTableService):
    def __init__(
        self,
        db_session: AsyncSession,
        storage_db_session: AsyncSession,
        storage_engine: AsyncEngine,
    ) -> None:
        self._db_session = db_session
        self._storage_db_session = storage_db_session
        self._metadata = MetaData()
        self._storage_engine = storage_engine

    async def fetch_rows(
        self,
        table: Table,
        limit: int = 100,
        offset: int = 0,
        ordering_params: list[OrderingParam] | None = None,
        filtering_params: list[FilteringParam] | None = None,
    ) -> list[Row]:
        sa_table = get_sa_table(table, self._metadata)
        stmt = select(sa_table).limit(limit).offset(offset)

        if ordering_params:
            stmt = _add_ordering_params_to_stmt(stmt, ordering_params)

        if filtering_params:
            stmt = _add_filtering_params_to_stmt(stmt, filtering_params)

        result = await self._storage_db_session.execute(stmt)
        rows = map_to_rows(table, cast(list[dict[str, Any]], result.mappings().all()))
        return rows

    async def create_table(self, table: UnSavedTable) -> Table:
        table_model = TableModel(
            name=table.name,
            verbose_name=table.verbose_name or table.name,
            description=table.description,
        )
        self._db_session.add(table_model)
        await self._db_session.flush()

        for f in table.fields:
            field_model = FieldModel(
                table_id=table_model.id,
                name=f.name,
                verbose_name=f.verbose_name,
                data_type=f.data_type,
                is_nullable=f.is_nullable,
                default_value=f.default_value,
            )
            # N+1 problem, but it's ok for now
            # Hackathon style code :)))
            self._db_session.add(field_model)
            await self._db_session.flush()

            if f.data_type is DataTypeEnum.CHOICE:
                for choice in f.choices:
                    choice_model = FieldChoiceModel(
                        field_id=field_model.id,
                        value=choice.value,
                    )
                    self._db_session.add(choice_model)

        await self._db_session.flush()
        saved_table = await self.get_table_by_id(table_model.id)

        sa_table = get_sa_table(saved_table, self._metadata)
        async with self._storage_engine.begin() as conn:
            await conn.run_sync(sa_table.create)

        return saved_table  # type: ignore[return-value]

    async def get_table_by_id(self, table_id: int) -> Table:
        """Возвращает доменную модель таблицы по её ID."""
        stmt = (
            select(TableModel)
            .filter_by(id=table_id)
            .options(selectinload(TableModel.fields))
        )
        result = await self._db_session.execute(stmt)
        table_model: TableModel | None = result.scalar_one_or_none()
        if not table_model:
            raise ValueError("There is no such table with id=%s" % table_id)

        return map_table_model_to_domain(table_model)

    async def update_table(self, table: Table) -> Table:
        """Обновляет метаданные таблицы."""
        stmt = (
            update(TableModel)
            .filter_by(id=table.table_id)
            .values(
                name=table.name,
                verbose_name=table.verbose_name,
                description=table.description,
            )
            .returning(TableModel.id)
        )
        await self._db_session.execute(stmt)
        await self._db_session.commit()
        return await self.get_table_by_id(table.table_id)  # type: ignore[return-value]

    async def delete_rows(self, table: Table, row_ids: list[int]) -> None:
        sa_table = get_sa_table(table, self._metadata)
        stmt = delete(sa_table).where(sa_table.c.id.in_(row_ids))
        await self._storage_db_session.execute(stmt)
        await self._storage_db_session.commit()

    async def insert_rows(self, rows: list[InsertRow]) -> list[Row]:
        if not rows:
            return []

        table = rows[0].table
        sa_table = get_sa_table(table, self._metadata)

        insert_values = []
        for r in rows:
            row_data = {}
            for rd in r.values:
                field = table.get_field_by_id(rd.field_id)
                if not field:
                    raise ValueError(
                        f"Field with id={rd.field_id} not found in table '{table.name}'",
                    )
                row_data[field.name] = rd.value.value
            insert_values.append(row_data)

        stmt = sa_table.insert().returning(sa_table)
        result = await self._storage_db_session.execute(stmt, insert_values)
        await self._storage_db_session.commit()

        return map_to_rows(table, cast(list[dict[str, Any]], result.mappings().all()))

    async def update_rows(self, rows: list[UpdateRow]) -> list[Row]:
        if not rows:
            return []

        table = rows[0].table
        sa_table = get_sa_table(table, self._metadata)

        updated_rows: list[Row] = []

        for r in rows:
            update_data = {}
            for rd in r.new_values:
                field = table.get_field_by_id(rd.field_id)
                if not field:
                    raise ValueError(
                        f"Field with id={rd.field_id} not found in table '{table.name}'",
                    )
                update_data[field.name] = rd.value.value

            stmt = (
                sa_table.update()
                .where(sa_table.c.id == r.row_id)
                .values(**update_data)
                .returning(sa_table)
            )
            result = await self._storage_db_session.execute(stmt)
            updated_rows.extend(
                map_to_rows(
                    table,
                    cast(list[dict[str, Any]], result.mappings().all()),
                ),
            )

        await self._storage_db_session.commit()
        return updated_rows

    async def count_rows(self, table: Table) -> int:
        sa_table = get_sa_table(table, self._metadata)
        stmt = select(func.count()).select_from(sa_table)
        result = await self._storage_db_session.execute(stmt)
        count = result.scalar_one()
        return int(count)

    async def get_tables_by_ids(self, table_ids: list[int]) -> list[Table]:
        if not table_ids:
            return []

        stmt = (
            select(TableModel)
            .where(TableModel.id.in_(table_ids))
            .options(selectinload(TableModel.fields).selectinload(FieldModel.choices))
        )
        result = await self._db_session.execute(stmt)
        table_models = result.scalars().all()

        tables: list[Table] = [map_table_model_to_domain(tm) for tm in table_models]

        return tables

    # TODO: Remove it after initializing Policies for namespaces and tables
    async def fetch_all_tables(self) -> list[Table]:
        """Возвращает список всех таблиц."""
        stmt = select(TableModel).options(
            selectinload(TableModel.fields).selectinload(FieldModel.choices)
        )
        result = await self._db_session.execute(stmt)
        table_models = result.scalars().all()
        return [map_table_model_to_domain(tm) for tm in table_models]

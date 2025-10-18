import pytest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from drawbridge_backend.domain.enums import DataTypeEnum
from drawbridge_backend.domain.tables.entities import (
    Field,
    UnSavedTable,
    InsertRow,
    RowData,
    IntValue,
    StringValue,
)
from drawbridge_backend.domain.impl.tables import SqlAlchemyTablesService


@pytest.mark.anyio
async def test_create_table_and_fetch(
    dbsession: AsyncSession,
    storage_dbsession: AsyncSession,
    storage_engine: AsyncEngine,
) -> None:
    service = SqlAlchemyTablesService(
        db_session=dbsession,
        storage_db_session=storage_dbsession,
        storage_engine=storage_engine,
    )

    # Создаём временную таблицу
    table_def = UnSavedTable(
        name="test_table",
        fields=[
            Field(
                _field_id=1,
                name="name",
                verbose_name="Name",
                data_type=DataTypeEnum.STRING,
                is_nullable=False,
            ),
            Field(
                _field_id=2,
                name="age",
                verbose_name="Age",
                data_type=DataTypeEnum.INT,
                is_nullable=True,
            ),
        ],
    )

    table = await service.create_table(table_def)
    assert table.table_id is not None
    assert len(table.fields) == 2


@pytest.mark.anyio
async def test_insert_and_fetch_rows(
    dbsession: AsyncSession,
    storage_dbsession: AsyncSession,
    storage_engine: AsyncEngine,
) -> None:
    service = SqlAlchemyTablesService(
        db_session=dbsession,
        storage_db_session=storage_dbsession,
        storage_engine=storage_engine,
    )

    # Создаём таблицу
    table_def = UnSavedTable(
        name="users",
        fields=[
            Field(
                _field_id=1,
                name="username",
                verbose_name="Username",
                data_type=DataTypeEnum.STRING,
                is_nullable=False,
            ),
            Field(
                _field_id=2,
                name="score",
                verbose_name="Score",
                data_type=DataTypeEnum.INT,
                is_nullable=True,
            ),
        ],
    )
    table = await service.create_table(table_def)

    # Вставляем строки
    rows_to_insert = [
        InsertRow(
            table=table,
            values=[
                RowData(field_id=1, value=StringValue("Alice")),
                RowData(field_id=2, value=IntValue(100)),
            ],
        ),
        InsertRow(
            table=table,
            values=[
                RowData(field_id=1, value=StringValue("Bob")),
                RowData(field_id=2, value=IntValue(150)),
            ],
        ),
    ]
    inserted_rows = await service.insert_rows(rows_to_insert)
    assert len(inserted_rows) == 2
    assert inserted_rows[0].values[0].value.value == "Alice"
    assert inserted_rows[1].values[1].value.value == 150

    # Проверяем count_rows
    count = await service.count_rows(table)
    assert count == 2


@pytest.mark.anyio
async def test_update_and_delete_rows(
    dbsession: AsyncSession,
    storage_engine: AsyncEngine,
    storage_dbsession: AsyncSession,
) -> None:
    service = SqlAlchemyTablesService(
        db_session=dbsession,
        storage_db_session=storage_dbsession,
        storage_engine=storage_engine,
    )

    # Создаём таблицу
    table_def = UnSavedTable(
        name="test-case",
        fields=[
            Field(
                _field_id=1,
                name="title",
                verbose_name="Title",
                data_type=DataTypeEnum.STRING,
                is_nullable=False,
            ),
            Field(
                _field_id=2,
                name="quantity",
                verbose_name="Quantity",
                data_type=DataTypeEnum.INT,
                is_nullable=False,
            ),
        ],
    )
    table = await service.create_table(table_def)

    # Вставляем строку
    row = InsertRow(
        table=table,
        values=[
            RowData(field_id=1, value=StringValue("Item1")),
            RowData(field_id=2, value=IntValue(10)),
        ],
    )
    inserted_rows = await service.insert_rows([row])
    row_id = inserted_rows[0].row_id

    # Обновляем строку
    from drawbridge_backend.domain.tables.entities import UpdateRow

    updated = await service.update_rows(
        [
            UpdateRow(
                table=table,
                row_id=row_id,
                new_values=[RowData(field_id=2, value=IntValue(20))],
            )
        ]
    )
    assert updated[0].values[1].value.value == 20

    # Удаляем строку
    await service.delete_rows(table, [row_id])
    count = await service.count_rows(table)
    assert count == 0

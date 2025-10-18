import pytest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from drawbridge_backend.domain.enums import DataTypeEnum
from drawbridge_backend.domain.impl.tables import SqlAlchemyTablesService
from drawbridge_backend.domain.tables.entities import (
    UnSavedTable,
    InsertRow,
    RowData,
    IntValue,
    StringValue,
    UnSavedField,
)


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
            UnSavedField(
                name="name",
                verbose_name="Name",
                data_type=DataTypeEnum.STRING,
                is_nullable=False,
            ),
            UnSavedField(
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
            UnSavedField(
                name="username",
                verbose_name="Username",
                data_type=DataTypeEnum.STRING,
                is_nullable=False,
            ),
            UnSavedField(
                name="score",
                verbose_name="Score",
                data_type=DataTypeEnum.INT,
                is_nullable=True,
            ),
        ],
    )
    table = await service.create_table(table_def)
    username_field_id = table.get_field_by_name("username").field_id
    score_field_id = table.get_field_by_name("score").field_id

    # Вставляем строки
    rows_to_insert = [
        InsertRow(
            table=table,
            values=[
                RowData(field_id=username_field_id, value=StringValue("Alice")),
                RowData(field_id=score_field_id, value=IntValue(100)),
            ],
        ),
        InsertRow(
            table=table,
            values=[
                RowData(field_id=username_field_id, value=StringValue("Bob")),
                RowData(field_id=score_field_id, value=IntValue(150)),
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

    fetched_rows = await service.fetch_rows(table)
    assert len(fetched_rows) == 2


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
            UnSavedField(
                name="title",
                verbose_name="Title",
                data_type=DataTypeEnum.STRING,
                is_nullable=False,
            ),
            UnSavedField(
                name="quantity",
                verbose_name="Quantity",
                data_type=DataTypeEnum.INT,
                is_nullable=False,
            ),
        ],
    )
    table = await service.create_table(table_def)

    title_field_id = table.get_field_by_name("title").field_id
    quantity_field_id = table.get_field_by_name("quantity").field_id

    # Вставляем строку
    row = InsertRow(
        table=table,
        values=[
            RowData(field_id=title_field_id, value=StringValue("Item1")),
            RowData(field_id=quantity_field_id, value=IntValue(10)),
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
                new_values=[RowData(quantity_field_id, value=IntValue(20))],
            )
        ]
    )
    assert updated[0].values[1].value.value == 20

    # Удаляем строку
    await service.delete_rows(table, [row_id])
    count = await service.count_rows(table)
    assert count == 0

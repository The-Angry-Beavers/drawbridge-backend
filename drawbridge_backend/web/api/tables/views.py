from fastapi import APIRouter

from drawbridge_backend.domain.tables.entities import UnSavedTable, InsertRow, UpdateRow
from drawbridge_backend.web.api.tables.schemas import (
    FetchRowsRequestSchema,
    FetchRowsResponseSchema,
    InsertRowsRequestSchema,
    InsertRowsResponseSchema,
    NameSpaceSchema,
    TableSchema,
    UpdateRowsRequestSchema,
    UpdateTableSchema,
    RowSchema,
    DeleteRowsRequestSchema,
)
from drawbridge_backend.web.dependencies.tables import TableServiceDep

router = APIRouter()


@router.get("/tables", tags=["tables"])
async def retrieve_tables(
    table_service: TableServiceDep,
    namespace_id: int | None = None,
) -> list[TableSchema]:
    """Retrieve all available for user tables."""
    return [
        TableSchema.model_validate(t, from_attributes=True)
        for t in await table_service.fetch_all_tables()
    ]


@router.get("/tables/{table_id}", tags=["tables"])
async def retrieve_table_by_id(
    table_id: int,
    table_service: TableServiceDep,
) -> TableSchema:
    """Retrieve a table by its ID."""
    table = await table_service.get_table_by_id(table_id)
    return TableSchema.model_validate(table, from_attributes=True)


@router.post("/tables", tags=["tables"])
async def create_table(
    table_service: TableServiceDep, request: UnSavedTable
) -> TableSchema:
    table = await table_service.create_table(request)
    return TableSchema.model_validate(table, from_attributes=True)


@router.patch("/tables/{table_id}", tags=["tables"])
async def update_table(table_id: int, req: UpdateTableSchema) -> TableSchema:
    """Retrieve a table by its ID."""
    raise NotImplementedError


@router.delete("/tables/{table_id}", tags=["tables"])
async def delete_table(table_id: int) -> None:
    """Delete a table by its ID."""
    raise NotImplementedError


@router.post("/tables/fetchRows", tags=["rows"])
async def fetch_table_rows(
    req: FetchRowsRequestSchema,
    table_service: TableServiceDep,
) -> FetchRowsResponseSchema:
    """Fetch rows from a table."""
    table = await table_service.get_table_by_id(req.table_id)
    rows = await table_service.fetch_rows(
        table=table,
        limit=req.limit,
        offset=req.offset,
        ordering_params=req.ordering_params,
        filtering_params=req.filter_params,
    )
    total_rows = await table_service.count_rows(table)

    return FetchRowsResponseSchema(
        total=total_rows,
        rows=[RowSchema.model_validate(r, from_attributes=True) for r in rows],
    )


@router.post("/tables/insertRows", tags=["rows"])
async def insert_table_rows(
    req: InsertRowsRequestSchema,
    table_service: TableServiceDep,
) -> InsertRowsResponseSchema:
    """Insert rows into a table."""
    is_success = True
    errors: list[str] = []

    try:
        table = await table_service.get_table_by_id(req.table_id)
        rows = [InsertRow(table, req_row.values) for req_row in req.rows]
        inserted_rows = await table_service.insert_rows(rows)
    except Exception as e:
        errors.append(str(e))
        is_success = False

    return InsertRowsResponseSchema(success=is_success, errors=errors)


async def delete_table_rows(
    req: DeleteRowsRequestSchema,
    table_service: TableServiceDep,
) -> InsertRowsResponseSchema:
    """Delete rows from a table."""
    is_success = True
    errors: list[str] = []

    try:
        table = await table_service.get_table_by_id(req.table_id)
        await table_service.delete_rows(table, req.row_ids)
    except Exception as e:
        errors.append(str(e))
        is_success = False

    return InsertRowsResponseSchema(success=is_success, errors=errors)


@router.post("/tables/updateRows", tags=["rows"])
async def update_table_row(
    req: UpdateRowsRequestSchema,
    table_service: TableServiceDep,
) -> InsertRowsResponseSchema:
    """Update a row in a table."""
    table = await table_service.get_table_by_id(req.table_id)
    is_success = True
    errors: list[str] = []

    try:
        table = await table_service.get_table_by_id(req.table_id)
        rows = [
            UpdateRow(table, req_row.row_id, req_row.new_values)
            for req_row in req.updated_rows
        ]
        inserted_rows = await table_service.update_rows(rows)
    except Exception as e:
        errors.append(str(e))
        is_success = False

    return InsertRowsResponseSchema(success=is_success, errors=errors)


@router.get("/namespaces", tags=["namespaces"])
async def retrieve_namespaces() -> list[NameSpaceSchema]:
    """Retrieve all available for user namespaces."""
    raise NotImplementedError


# @router.delete("/tables/deleteField", tags=["fields"])
# async def delete_table_field(req: DeleteFieldSchema) -> TableSchema:
#     """Delete a field from a table."""
#     raise NotImplementedError
#
#
# @router.patch("/tables/updateField", tags=["fields"])
# async def update_table_field(req: UpdateFieldSchema) -> TableSchema:
#     """
#     Update a field in a table.
#     """
#     raise NotImplementedError
#
#
# @router.post("/tables/addField", tags=["fields"])
# async def add_table_field(req: AddFieldSchema) -> FieldSchema:
#     """Add a field to a table."""
#     raise NotImplementedError

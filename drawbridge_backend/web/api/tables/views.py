from fastapi import APIRouter

from drawbridge_backend.web.api.tables.schemas import (
    TableSchema,
    UpdateTableSchema,
    FetchRowsRequestSchema,
    FetchRowsResponseSchema,
    InsertRowsResponseSchema,
    InsertRowsRequestSchema,
    UpdateRowsRequestSchema,
    NameSpaceSchema,
    DeleteFieldSchema,
    UpdateFieldSchema,
    AddFieldSchema,
    FieldSchema,
)
from drawbridge_backend.web.dependencies.tables import TableServiceDep

router = APIRouter()


@router.get("/tables", tags=["tables"])
async def retrieve_tables(
    namespace_id: int, table_service: TableServiceDep
) -> list[TableSchema]:
    """Retrieve all available for user tables."""
    return [
        TableSchema.model_validate(t, from_attributes=True)
        for t in await table_service.fetch_all_tables()
    ]


@router.patch("/tables/{table_id}", tags=["tables"])
async def update_table(table_id: int, req: UpdateTableSchema) -> TableSchema:
    """Retrieve a table by its ID."""
    raise NotImplementedError()


@router.delete("/tables/{table_id}", tags=["tables"])
async def delete_table(table_id: int) -> None:
    """Delete a table by its ID."""
    raise NotImplementedError()


@router.post("/tables/fetchRows", tags=["rows"])
async def fetch_table_rows(req: FetchRowsRequestSchema) -> FetchRowsResponseSchema:
    """Fetch rows from a table."""
    raise NotImplementedError()


@router.post("/tables/insertRows", tags=["rows"])
async def insert_table_rows(req: InsertRowsRequestSchema) -> InsertRowsResponseSchema:
    """Insert rows into a table."""
    raise NotImplementedError()


@router.post("/tables/updateRows", tags=["rows"])
async def update_table_row(req: UpdateRowsRequestSchema) -> InsertRowsResponseSchema:
    """Update a row in a table."""
    raise NotImplementedError()


@router.get("/namespaces", tags=["namespaces"])
async def retrieve_namespaces() -> list[NameSpaceSchema]:
    """Retrieve all available for user namespaces."""
    raise NotImplementedError()


@router.delete("/tables/deleteField", tags=["fields"])
async def delete_table_field(req: DeleteFieldSchema) -> TableSchema:
    """Delete a field from a table."""
    raise NotImplementedError()


@router.patch("/tables/updateField", tags=["fields"])
async def update_table_field(req: UpdateFieldSchema) -> TableSchema:
    """
    Update a field in a table.
    """
    raise NotImplementedError()


@router.post("/tables/addField", tags=["fields"])
async def add_table_field(req: AddFieldSchema) -> FieldSchema:
    """Add a field to a table."""
    raise NotImplementedError()

from fastapi import APIRouter

from drawbridge_backend.web.api.tables.schemas import (
    TableSchema,
    FetchRowsRequestSchema,
    FetchRowsResponseSchema,
    NameSpaceSchema,
    InsertRowsResponseSchema,
    InsertRowsRequestSchema,
    UpdateRowsRequestSchema,
    UpdateFieldSchema,
    FieldSchema,
    AddFieldSchema,
    UpdateTableSchema, DeleteFieldSchema,
)

router = APIRouter()


# @router.get("/tables", tags=["tables"])
# async def retrieve_tables(namespace_id: int) -> list[TableSchema]:
#     """Retrieve all available for user tables."""
#     pass
#
#
# @router.patch("/tables/{table_id}", tags=["tables"])
# async def update_table(table_id: int, req: UpdateTableSchema) -> TableSchema:
#     """Retrieve a table by its ID."""
#     pass
#
#
# @router.delete("/tables/{table_id}", tags=["tables"])
# async def delete_table(table_id: int) -> None:
#     """Delete a table by its ID."""
#     pass
#
#
# @router.post("/tables/fetchRows", tags=["rows"])
# async def fetch_table_rows(req: FetchRowsRequestSchema) -> FetchRowsResponseSchema:
#     """Fetch rows from a table."""
#     pass
#
#
# @router.post("/tables/insertRows", tags=["rows"])
# async def insert_table_rows(req: InsertRowsRequestSchema) -> InsertRowsResponseSchema:
#     """Insert rows into a table."""
#     pass
#
#
# @router.post("/tables/updateRows", tags=["rows"])
# async def update_table_row(req: UpdateRowsRequestSchema) -> InsertRowsResponseSchema:
#     """Update a row in a table."""
#     pass
#
#
# @router.get("/namespaces", tags=["namespaces"])
# async def retrieve_namespaces() -> list[NameSpaceSchema]:
#     """Retrieve all available for user namespaces."""
#     pass
#
#
# @router.delete("/tables/deleteField", tags=["fields"])
# async def delete_table_field(req: DeleteFieldSchema) -> TableSchema:
#     """Delete a field from a table."""
#     pass
#
#
# @router.patch("/tables/updateField", tags=["fields"])
# async def update_table_field(req: UpdateFieldSchema) -> TableSchema:
#     """
#     Update a field in a table.
#     """
#     pass
#
#
# @router.post("/tables/addField", tags=["fields"])
# async def add_table_field(req: AddFieldSchema) -> FieldSchema:
#     """Add a field to a table."""
#     pass

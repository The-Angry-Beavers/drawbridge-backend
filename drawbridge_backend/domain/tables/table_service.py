import abc

from drawbridge_backend.domain.tables.entities import (
    OrderingParam,
    FilteringParam,
    InsertRow,
    Row,
    UpdateRow,
    Table,
    UnSavedTable,
)


class AbstractTableService(abc.ABC):
    """
    Abstract service for table operations.
    Defines the interface for fetching, inserting, updating, and deleting rows in tables.
    There is no repository layer for Table as it directly interacts with the storage database.
    and logic hardly differs between different storage backends due to ACID between metadata and shemas.
    """

    @abc.abstractmethod
    async def fetch_rows(
        self,
        table: Table,
        limit: int = 100,
        offset: int = 0,
        ordering_params: list[OrderingParam] | None = None,
        filtering_params: list[FilteringParam] | None = None,
    ) -> list[Row]:
        """Fetch rows from a table.

        :param table: The table to fetch rows from.
        :param limit: Maximum number of rows to fetch.
        :param offset: Number of rows to skip before starting to fetch.
        :param ordering_params: List of ordering parameters.
        :param filtering_params: List of filtering parameters. Casts as OR conditions.
        :return: List of rows as dictionaries.
        """
        pass

    async def fetch_row_by_id(
        self,
        table: Table,
        row_id: int,
    ) -> Row | None:
        """Fetch a single row from a table by its ID.

        :param table: table to fetch the row from.
        :param row_id: ID of the row to fetch.
        :return: Row as a dictionary or None if not found.
        """
        rows = await self.fetch_rows(
            table=table,
            limit=1,
            offset=0,
            filtering_params=[
                FilteringParam(field_id=0, value=str(row_id))
            ],  # Assuming field_id=0 is the row ID field
        )
        if rows:
            return rows[0]
        return None

    @abc.abstractmethod
    async def insert_rows(
        self,
        rows: list[InsertRow],
    ) -> list[Row]:
        """Insert rows into a table.

        :param rows: List of rows to insert.
        """
        pass

    async def insert_row(
        self,
        row: InsertRow,
    ) -> Row:
        """Insert a single row into a table.

        :param row: Row to insert.
        """
        rows = await self.insert_rows([row])
        return rows[-1]

    @abc.abstractmethod
    async def update_rows(
        self,
        rows: list[UpdateRow],
    ) -> list[Row]:
        """Update rows in a table.

        :param rows: List of rows to update.
        """
        pass

    async def update_row(
        self,
        row: UpdateRow,
    ) -> Row:
        """Update a single row in a table.

        :param row: Row to update.
        """
        rows = await self.update_rows([row])
        return rows[-1]

    @abc.abstractmethod
    async def delete_rows(
        self,
        table: Table,
        row_ids: list[int],
    ) -> None:
        """Delete rows from a table.

        :param table: table to delete rows from.
        :param row_ids: List of row IDs to delete.
        """
        pass

    async def delete_row(
        self,
        table: Table,
        row_id: int,
    ) -> None:
        """Delete a single row from a table.

        :param table: table to delete the row from.
        :param row_id: ID of the row to delete.
        """
        await self.delete_rows(table, [row_id])

    @abc.abstractmethod
    async def update_table(self, table: Table) -> Table:
        """Update table metadata and schema in storage db"""
        pass

    @abc.abstractmethod
    async def create_table(self, table: UnSavedTable) -> Table:
        """Create table metadata and schema in storage db"""
        pass

    @abc.abstractmethod
    async def get_table_by_id(self, table_id: int) -> Table | None:
        """Get table metadata by ID"""
        pass

    @abc.abstractmethod
    async def count_rows(self, table: Table) -> int:
        pass

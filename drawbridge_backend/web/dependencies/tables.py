from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from drawbridge_backend.db.dependencies import (
    get_storage_db_engine,
    get_storage_db_session,
    get_db_session,
)
from drawbridge_backend.domain.impl.tables import SqlAlchemyTablesService


def get_tables_service(
    storage_db_engine: Annotated[AsyncEngine, Depends(get_storage_db_engine)],
    storage_db_session: Annotated[AsyncSession, Depends(get_storage_db_session)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SqlAlchemyTablesService:
    return SqlAlchemyTablesService(
        db_session,
        storage_db_session,
        storage_db_engine,
    )


TableServiceDep = Annotated[SqlAlchemyTablesService, Depends(get_tables_service)]

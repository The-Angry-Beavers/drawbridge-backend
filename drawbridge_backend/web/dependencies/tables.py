from fastapi.params import Depends

from drawbridge_backend.db.dependencies import get_storage_db_engine
from drawbridge_backend.domain.impl.tables import SqlAlchemyTablesService


def get_tables_service() -> SqlAlchemyTablesService:
    raise NotImplementedError()

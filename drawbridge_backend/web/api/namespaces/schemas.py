from pydantic import BaseModel

from drawbridge_backend.web.api.tables.schemas import TableSchema


class NameSpaceSchema(BaseModel):

    id: int
    name: str
    description: str | None
    tables: list[TableSchema]

class CreateNameSpaceSchema(BaseModel):

    name: str
    description: str | None = None

class UpdateNameSpaceSchema(BaseModel):
    name: str | None = None
    description: str | None = None



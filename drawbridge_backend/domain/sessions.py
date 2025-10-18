import dataclasses
import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from drawbridge_backend.db.models.edit_session import EditSessionModel
from drawbridge_backend.domain.tables.entities import Table


@dataclasses.dataclass
class Session:
    id: int
    user_id: UUID
    table_id: int
    created_at: datetime.datetime
    expires_at: datetime.datetime
    is_closed: bool

    @classmethod
    def from_orm(cls, model: "EditSessionModel") -> "Session":
        return cls(
            id=model.id,
            user_id=model.user_id,
            table_id=model.table_id,
            created_at=model.created_at,
            expires_at=model.expires_at,
            is_closed=model.is_closed,
        )


K = TypeVar("K")
V = TypeVar("V")

def _drop_none_from_dict(d: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in d.items() if v is not None}


async def _close_expired_sessions(session: AsyncSession) -> None:
    """Close all expired sessions."""
    stmt = (
        update(EditSessionModel)
        .where(
            EditSessionModel.expires_at < datetime.datetime.utcnow(),
        )
        .values(is_closed=True)
    )
    await session.execute(stmt)


async def get_list_of_sessions(
    session: AsyncSession,
    table_id: int | None = None,
    user_id: UUID | None = None,
    is_closed: bool | None = None,
) -> list[Session]:
    """Retrieve all sessions for a given table."""

    # Close expired sessions first
    await _close_expired_sessions(session)

    stmt = select(EditSessionModel)
    filters_by = {"table_id": table_id, "user_id": user_id, "is_closed": is_closed}
    filters_by = _drop_none_from_dict(filters_by)
    stmt = stmt.filter_by(**filters_by)
    result = await session.execute(stmt)
    models = result.scalars().all()
    return [Session.from_orm(model) for model in models]


async def get_open_sessions_for_table(
    db_session: AsyncSession, table: Table
) -> list[Session]:
    """Retrieve all open sessions for a given table."""
    return await get_list_of_sessions(
        session=db_session,
        table_id=table.table_id,
        is_closed=False,
    )


async def get_open_sessions_for_user(
    db_session: AsyncSession, user_id: UUID
) -> list[Session]:
    """Retrieve an open session for a given user and table."""

    sessions = await get_list_of_sessions(
        session=db_session,
        user_id=user_id,
        is_closed=False,
    )

    return sessions


@dataclasses.dataclass
class CreateSession:
    user_id: UUID
    table_id: int


async def create_session(db_session: AsyncSession, create: CreateSession) -> Session:
    """Create a new edit session."""
    expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
    model = EditSessionModel(
        user_id=create.user_id,
        table_id=create.table_id,
        expires_at=expires_at,
        is_closed=False,
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)
    return Session.from_orm(model)


async def close_session(db_session: AsyncSession, session_id: int) -> None:
    """Close an edit session."""
    stmt = update(EditSessionModel).filter_by(id=session_id).values(is_closed=True)
    await db_session.execute(stmt)
    await db_session.commit()

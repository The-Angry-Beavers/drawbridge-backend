import dataclasses
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from drawbridge_backend.db.dependencies import SessionDep
from drawbridge_backend.db.models.users import User, current_active_user  # type: ignore
from drawbridge_backend.domain.sessions import (
    Session,
    get_list_of_sessions,
    get_open_sessions_for_user,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


CurrentUserDep = Annotated[User, Depends(current_active_user)]


@router.get("/me")
async def get_sessions(user: CurrentUserDep, session: SessionDep) -> list[Session]:
    """Retrieve all sessions."""
    return await get_open_sessions_for_user(session, user.id)


@router.get("")
async def list_sessions(
    session: SessionDep,
    table_id: int | None = None,
    user_id: UUID | None = None,
    is_closed: bool | None = None,
) -> list[Session]:
    """List all sessions."""
    return await get_list_of_sessions(session, table_id, user_id, is_closed)


@dataclasses.dataclass
class CreateSessionRequestBody:
    table_id: int


@router.post("")
async def create_session(
    session: SessionDep,
    current_user: CurrentUserDep,
    request_body: CreateSessionRequestBody,
) -> Session:
    """Create a new session."""
    from drawbridge_backend.domain.sessions import CreateSession, create_session

    create_command = CreateSession(
        user_id=current_user.id,
        table_id=request_body.table_id,
    )
    return await create_session(session, create_command)


@router.get("/{session_id}/close")
async def get_session(
    session: SessionDep,
    session_id: int,
) -> None:
    """Retrieve a session by ID."""
    from drawbridge_backend.domain.sessions import close_session

    return await close_session(session, session_id)

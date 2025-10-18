from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from starlette.requests import Request


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    finally:
        await session.commit()
        await session.close()


async def get_storage_db_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get storage database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.storage_db_session_factory()

    try:
        yield session
    finally:
        await session.commit()
        await session.close()


async def get_storage_db_engine(
    request: Request,
) -> AsyncGenerator[AsyncEngine, None]:

    engine: AsyncEngine = request.app.state.storage_db_engine

    try:
        yield engine
    finally:
        pass

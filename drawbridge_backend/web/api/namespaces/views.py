from collections.abc import Sequence

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from drawbridge_backend.db.dependencies import SessionDep
from drawbridge_backend.db.models.tables import NameSpaceModel, TableModel, FieldModel
from drawbridge_backend.db.models.users import User  # type: ignore
from drawbridge_backend.web.api.namespaces.schemas import (
    NameSpaceSchema,
    CreateNameSpaceSchema,
    UpdateNameSpaceSchema,
)
from drawbridge_backend.web.api.sessions import CurrentUserDep

router = APIRouter()


class NameSpaceNotFound(HTTPException):

    def __init__(self, namespace_id: int):
        super().__init__(
            status_code=404,
            detail=f"Namespace with ID '{namespace_id}' not found.",
        )


def _filter_namespaces_for_user(
    auth_user: User, stmt: Select[tuple[NameSpaceModel]]
) -> Select[tuple[NameSpaceModel]]:
    # TODO: применить фильтры, например:
    return stmt


# Опасное дерьмо
NAMESPACE_LOAD_OPTS = (
    selectinload(NameSpaceModel.tables)
    .selectinload(TableModel.fields)
    .selectinload(FieldModel.choices)
)


async def _fetch_namespaces(
    auth_user: User, session: AsyncSession
) -> Sequence[NameSpaceModel]:
    stmt = select(NameSpaceModel)
    stmt = _filter_namespaces_for_user(auth_user, stmt)
    stmt = stmt.options(NAMESPACE_LOAD_OPTS)
    result = await session.execute(stmt)
    return result.scalars().all()


async def _get_namespace_by_id(
    namespace_id: int, session: AsyncSession
) -> NameSpaceModel | None:
    stmt = (
        select(NameSpaceModel).filter_by(id=namespace_id).options(NAMESPACE_LOAD_OPTS)
    )
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()
    if instance is None:
        raise NameSpaceNotFound(namespace_id)

    return instance


@router.get("/namespaces", tags=["namespaces"])
async def list_namespaces(
    session: SessionDep, auth_user: CurrentUserDep
) -> list[NameSpaceSchema]:
    """List all available namespaces for user"""
    return [
        NameSpaceSchema.model_validate(ns, from_attributes=True)
        for ns in await _fetch_namespaces(auth_user, session)
    ]


@router.post("/namespaces", tags=["namespaces"])
async def create_namespace(
    request: CreateNameSpaceSchema, session: SessionDep
) -> NameSpaceSchema:
    """Create namespace"""
    model_instance = NameSpaceModel(
        name=request.name,
        description=request.description,
    )
    session.add(model_instance)
    await session.commit()
    return NameSpaceSchema.model_validate(model_instance, from_attributes=True)


@router.patch("/namespaces/{namespace_id}", tags=["namespaces"])
async def partial_update_namespace(
    namespace_id: int, request: UpdateNameSpaceSchema, session: SessionDep
) -> NameSpaceSchema:
    """Update namespace"""
    namespace_instance = _get_namespace_by_id(namespace_id, session)
    for attr, val in request.model_dump(exclude_unset=True).items():
        setattr(namespace_instance, attr, val)
    session.add(namespace_instance)
    await session.commit()
    namespace_instance = _get_namespace_by_id(namespace_id, session)
    return NameSpaceSchema.model_validate(
        namespace_instance,
        from_attributes=True,
    )


@router.patch("/namespaces/{namespace_id}", tags=["namespaces"])
async def delete_namespace(namespace_id: int, session: SessionDep) -> None:
    """Delete namespace"""
    namespace_instance = _get_namespace_by_id(namespace_id, session)
    await session.delete(namespace_instance)
    await session.commit()
    return

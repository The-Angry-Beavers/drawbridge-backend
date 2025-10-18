import dataclasses

from fastapi import APIRouter
from sqlalchemy import select

from drawbridge_backend.db.dependencies import SessionDep
from drawbridge_backend.db.models.permissions import NameSpacePermissionModel
from drawbridge_backend.web.api.sessions import CurrentUserDep

router = APIRouter()


@dataclasses.dataclass
class PermissionResponseModel:
    can_edit: bool
    can_read: bool
    can_delete: bool


@dataclasses.dataclass
class InverterPermissionResponseModel:
    is_edit_disabled: bool
    is_read_disabled: bool
    is_delete_disabled: bool


@router.get("/namespaces/{namespace_id}/permissions")
async def get_namespace_permissions(
    namespace_id: int,
    current_user=CurrentUserDep,
    session=SessionDep,
) -> PermissionResponseModel:
    query = select(NameSpacePermissionModel).filter_by(
        namespace_id=namespace_id,
        user_id=current_user.id,
    )
    result = await session.execute(query)
    permission = result.scalar_one_or_none()
    if not permission:
        return PermissionResponseModel(
            **{
                "can_edit": False,
                "can_read": False,
                "can_delete": False,
            }
        )
    return PermissionResponseModel(
        **{
            "can_edit": permission.can_edit,
            "can_read": permission.can_read,
            "can_delete": permission.can_delete,
        }
    )


@router.get("/tables/{table_id}/permissions")
async def get_table_permissions(
    table_id: int,
    current_user=CurrentUserDep,
    session=SessionDep,
):
    query = select(NameSpacePermissionModel).filter_by(
        table_id=table_id,
        user_id=current_user.id,
    )
    result = await session.execute(query)
    permission = result.scalar_one_or_none()
    if not permission:
        return {
            "is_edit_disabled": False,
            "is_read_disabled": False,
            "is_delete_disabled": False,
        }


@router.get("/fields/{field_id}/permissions")
async def get_field_permissions(
    field_id: int,
    current_user=CurrentUserDep,
    session=SessionDep,
):
    query = select(NameSpacePermissionModel).filter_by(
        field_id=field_id,
        user_id=current_user.id,
    )
    result = await session.execute(query)
    permission = result.scalar_one_or_none()
    if not permission:
        return {
            "is_edit_disabled": False,
            "is_read_disabled": False,
            "is_delete_disabled": False,
        }
    return {
        "is_edit_disabled": permission.is_edit_disabled,
        "is_read_disabled": permission.is_read_disabled,
        "is_delete_disabled": permission.is_delete_disabled,
    }

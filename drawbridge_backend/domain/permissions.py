from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from drawbridge_backend.db.models.permissions import (
    TablePermissionModel,
    FieldPermissionModel,
    NameSpacePermissionModel,
)
from drawbridge_backend.db.models.tables import TableModel


class PermissionChecker:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_permission(self, model, **filters):
        """Общий метод для получения записи о разрешении."""
        query = select(model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_table(self, table_id: int) -> TableModel:
        """Получить объект таблицы по ID."""
        query = select(TableModel).filter_by(id=table_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def _check_permission(
        self,
        model,
        user_id: UUID,
        object_field: str,
        object_id: int,
        edit_attr: str,
        fallback_func,
    ) -> bool:
        """
        Общий метод для проверки прав на объект (таблица, поле, пространство имён).
        - model: модель разрешений (TablePermissionModel, FieldPermissionModel и т.д.)
        - object_field: имя поля, связанного с объектом (например, 'table_id')
        - object_id: идентификатор объекта
        - edit_attr: имя атрибута для проверки (например, 'is_edit_disabled' или 'is_read_disabled')
        - fallback_func: функция, которую нужно вызвать, если разрешения не найдены
        """
        permission = await self._get_permission(
            model, **{object_field: object_id, "user_id": user_id}
        )
        if not permission:
            return await fallback_func()

        return not getattr(permission, edit_attr)

    # --- Методы для таблиц ---

    async def user_can_edit_table(self, user_id: UUID, table_id: int) -> bool:
        async def fallback():
            table = await self._get_table(table_id)
            if not table.namespace_id:
                return True
            return await self.user_can_edit_namespace(user_id, table.namespace_id)

        return await self._check_permission(
            TablePermissionModel,
            user_id,
            "table_id",
            table_id,
            "is_edit_disabled",
            fallback,
        )

    async def user_can_view_table(self, user_id: UUID, table_id: int) -> bool:
        async def fallback():
            table = await self._get_table(table_id)
            if not table.namespace_id:
                return False
            return await self.user_can_edit_namespace(user_id, table.namespace_id)

        return await self._check_permission(
            TablePermissionModel,
            user_id,
            "table_id",
            table_id,
            "is_read_disabled",
            fallback,
        )

    # --- Методы для колонок ---

    async def user_can_edit_column(self, user_id: UUID, field_id: int) -> bool:
        async def fallback():
            return await self.user_can_edit_table(user_id, field_id)

        return await self._check_permission(
            FieldPermissionModel,
            user_id,
            "field_id",
            field_id,
            "is_edit_disabled",
            fallback,
        )

    async def user_can_view_column(self, user_id: UUID, field_id: int) -> bool:
        async def fallback():
            return await self.user_can_edit_table(user_id, field_id)

        return await self._check_permission(
            FieldPermissionModel,
            user_id,
            "field_id",
            field_id,
            "is_read_disabled",
            fallback,
        )

    # --- Методы для namespace ---

    async def user_can_edit_namespace(self, user_id: UUID, namespace_id: int) -> bool:
        permission = await self._get_permission(
            NameSpacePermissionModel, namespace_id=namespace_id, user_id=user_id
        )
        return bool(permission and permission.can_edit)

    async def user_can_view_namespace(self, user_id: UUID, namespace_id: int) -> bool:
        permission = await self._get_permission(
            NameSpacePermissionModel, namespace_id=namespace_id, user_id=user_id
        )
        return permission is not None

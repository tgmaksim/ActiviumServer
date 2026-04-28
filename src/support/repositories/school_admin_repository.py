from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_admin_model import SchoolAdmin

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolAdminRepository']


class SchoolAdminRepository(SqlAlchemyRepository[SchoolAdmin]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolAdmin)

    async def create_admin(
            self,
            user_id: int,
            name: str,
            parent_admin_id: Optional[int],
            person_id: Optional[int],
            school_id: Optional[int],
            dnevnik_token: Optional[str]
    ):
        await self.create({
            'user_id': user_id,
            'name': name,
            'parent_admin_id': parent_admin_id,
            'person_id': person_id,
            'school_id': school_id,
            'dnevnik_token': dnevnik_token
        }, security=['user_id'])

    async def get_admin(self, user_id: int) -> Optional[SchoolAdmin]:
        return await self.get_single(SchoolAdmin.user_id == user_id)

    async def get_my_admins(self, user_id: int) -> list[SchoolAdmin]:
        return await self.get_multi(SchoolAdmin.parent_admin_id == user_id)

    async def add_my_admins(self, user_id: int, admins: list[tuple[int, str]]) -> list[SchoolAdmin]:
        return await self.create_many([{
            'user_id': admin_id,
            'name': admin_name[:64],
            'parent_admin_id': user_id
        } for admin_id, admin_name in admins], security=['user_id'], security_nothing=True)

    async def delete_my_admin(self, user_id: int, admin_id):
        return await self.delete(SchoolAdmin.user_id == admin_id, SchoolAdmin.parent_admin_id == user_id)
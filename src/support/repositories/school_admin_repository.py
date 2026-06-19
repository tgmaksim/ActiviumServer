from typing import Optional
from datetime import timedelta

from sqlalchemy.sql import select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.sql.functions import func

from ...dependencies.httpx import get_httpx_client
from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from ...repositories.db_queue import AsyncDBQueue
from ...models.school_admin_model import SchoolAdmin

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolAdminRepository']


class SchoolAdminRepository(SqlAlchemyRepository[SchoolAdmin]):
    """Репозиторий для взаимодействия с администраторами образовательных организаций"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolAdmin)

    async def create_admin(
            self,
            user_id: int,
            name: str,
            parent_admin_id: Optional[int],
            person_id: Optional[int],
            school_id: Optional[int],
            timezone: Optional[int],
            dnevnik_token: Optional[str]
    ) -> SchoolAdmin:
        """
        Добавление старшего администратора образовательной организации

        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :param name: имя администратора образовательной организации
        :param parent_admin_id: идентификатор администратора образовательной организации верхнего уровня
        :param person_id: идентификатор персоны в Дневнике.ру для старшего администратора
        :param school_id: идентификатор образовательной организации для старшего администратора
        :param timezone: часовой пояс в секундах для старшего администратора
        :param dnevnik_token: API-токен Дневника.ру для старшего администратора
        :return: добавленный администратор образовательной организации
        """

        return await self.create({
            'user_id': user_id,
            'name': name,
            'parent_admin_id': parent_admin_id,
            'person_id': person_id,
            'school_id': school_id,
            'timezone': timezone,
            'dnevnik_token': dnevnik_token,
            'life': True if parent_admin_id is None else None
        }, security=['user_id'])

    async def get_admin(self, user_id: int, only_life: bool = True) -> Optional[SchoolAdmin]:
        """
        Получение администратора образовательной организации

        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :param only_life: только работающие сессии администратора образовательной организации с флагом life=true
        :return: администратор образовательной организации, если существует
        """

        if not only_life:
            statement = (
                select(SchoolAdmin)
                .where(SchoolAdmin.user_id == user_id)
            )
        else:
            Root = aliased(SchoolAdmin)

            statement = (
                select(SchoolAdmin)
                .join(
                    Root,
                    Root.user_id == func.get_root_admin_id(SchoolAdmin.user_id)  # Получения старшего администратора
                )
                .where(
                    SchoolAdmin.user_id == user_id,
                    Root.life.is_(True)  # Проверка статуса старшего администратора
                )
            )

        statement = statement.options(selectinload(SchoolAdmin.parent_admin))

        result = await self.queue.execute(statement)
        return result.scalar_one_or_none()

    async def get_my_admins(self, user_id: int) -> list[SchoolAdmin]:
        """
        Получение дочерних администраторов образовательной организации

        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :return: список дочерних администраторов образовательной организации
        """

        return await self.get_multi(SchoolAdmin.parent_admin_id == user_id)

    async def add_my_admins(self, user_id: int, admins: list[tuple[int, str]]) -> list[SchoolAdmin]:
        """
        Добавление дочерних администраторов образовательной организации

        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :param admins: дочерние администраторы образовательной организации (идентификатор Telegram-аккаунта, имя)
        :return: добавленные администраторы образовательной организации
        """

        return await self.create_many([{
            'user_id': admin_id,
            'name': admin_name[:64],
            'parent_admin_id': user_id
        } for admin_id, admin_name in admins], security=['user_id'], security_nothing=True)

    async def delete_my_admin(self, user_id: int, admin_id):
        """
        Удалить дочернего администратора образовательной организации

        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :param admin_id: идентификатор Telegram-аккаунта дочернего администратора образовательной организации
        """

        return await self.delete(SchoolAdmin.user_id == admin_id, SchoolAdmin.parent_admin_id == user_id)

    async def kill_old_admins(self, lifetime: timedelta) -> list[SchoolAdmin]:
        """
        Пометить старые сессии администраторов неработающими

        :param lifetime: время жизни сессии администратора
        """

        return await self.update_many(
            {'life': False},
            SchoolAdmin.parent_admin_id.is_(None),
            (func.now() - SchoolAdmin.updated_at) > lifetime
        )

    async def check_auth(self, user_id: int, dnr: Optional[AioDnevnikruApi] = None) -> bool:
        """
        Проверить авторизацию сессии администратора образовательной организации в Дневнике.ру

        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :return: статус авторизации сессии в Дневнике.ру
        """

        school_admin = await self.get_single(SchoolAdmin.user_id == user_id)
        if school_admin is None:
            return False

        dnr = dnr or AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)

        try:
            await dnr.get_context()
        except DnevnikruApiException:
            return False
        return True

    async def kill_admin(self, user_id: int) -> Optional[SchoolAdmin]:
        """
        Пометить сессию старшего администратора образовательной организации неработающей

        :param user_id: идентификатор администратора образовательной организации
        :return: обновленный администратор образовательной организации
        """

        await self.update({'life': False}, SchoolAdmin.user_id == func.get_root_admin_id(user_id))

        return await self.get_admin(user_id, only_life=False)

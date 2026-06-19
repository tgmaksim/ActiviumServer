from typing import Optional
from datetime import timedelta

from sqlalchemy import func

from dnevnikru import AioDnevnikruApi
from ...dependencies.httpx import get_httpx_client
from dnevnikru.exceptions import DnevnikruApiException

from ...models.session_model import Session
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SessionRepository']


class SessionRepository(SqlAlchemyRepository[Session]):
    """Репозиторий для взаимодействия с сессиями пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Session)

    async def create_session(self, session_id: str) -> Session:
        """
        Создать неавторизованную сессию

        :param session_id: идентификатор сессии
        :return: созданная сессия
        """

        return await self.create({
            'session_id': session_id
        })

    async def get_session(self, session_id: str, only_life: bool = True) -> Optional[Session]:
        """
        Получить сессию по идентификатору

        :param session_id: идентификатор сессии
        :param only_life: только работающие сессии с флагом life=true
        :return: сессия, если существует
        """

        return await self.get_single(
            Session.session_id == session_id,
            *((Session.life == True,) if only_life else ())
        )

    async def get_sessions(self, parent_id: int) -> list[Session]:
        """
        Получить все работающие сессии пользователя

        :param parent_id: идентификатор пользователя
        :return: список работающих сессий
        """

        return await self.get_multi(Session.parent_id == parent_id, Session.life == True)

    async def auth_session(
            self,
            session_id: str,
            dnevnik_token: str,
            parent_id: int,
            active_child_id: int
    ) -> Optional[Session]:
        """
        Авторизовать сессию пользователя

        :param session_id: идентификатор сессии
        :param dnevnik_token: API-токен Дневника.ру для взаимодействия с ним
        :param parent_id: идентификатор пользователя
        :param active_child_id: идентификатор активного ребенка (профиля)
        :return: авторизованная сессия, если существует
        """

        return await self.update({
            'parent_id': parent_id,
            'active_child_id': active_child_id,
            'dnevnik_token': dnevnik_token,
            'life': True
        }, Session.session_id == session_id)

    async def update_firebase(self, session_id: str, firebase_token: str) -> Optional[Session]:
        """
        Обновить Firebase-токен сессии пользователя

        :param session_id: идентификатор сессии
        :param firebase_token: Firebase-токен для уведомлений
        :return: обновленная сессия пользователя
        """

        return await self.update({
            'firebase_token': firebase_token
        }, Session.session_id == session_id)

    async def set_active_child(self, session_id: str, active_child_id: int) -> Optional[Session]:
        """
        Изменить активного ребенка (профиля) у сессии пользователя

        :param session_id: идентификатор сессии
        :param active_child_id: идентификатор ребенка (профиля)
        :return: обновленная сессия, если существует
        """

        return await self.update({
            'active_child_id': active_child_id
        }, Session.session_id == session_id)

    async def kill_session(self, session_id: str) -> Optional[Session]:
        """
        Пометить сессию как неработающую с флагом life=false

        :param session_id: идентификатор сессии
        :return: обновленная сессия, если существует
        """

        return await self.update({'life': False}, Session.session_id == session_id)

    async def check_session_auth(self, session_id: str, dnr: AioDnevnikruApi = None) -> bool:
        """
        Проверить авторизацию сессии пользователя в Дневнике.ру

        :param session_id: идентификатор сессии
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :return: статус авторизации сессии в Дневнике.ру
        """

        session = await self.get_session(session_id)
        if session is None:
            return False

        dnr = dnr or AioDnevnikruApi(get_httpx_client(), session.dnevnik_token)

        try:
            await dnr.get_context()
        except DnevnikruApiException:
            return False
        return True

    async def kill_old_sessions(self, lifetime: timedelta) -> list[Session]:
        """
        Пометить старые сессии неработающими

        :param lifetime: время жизни сессии
        """

        return await self.update_many({'life': False}, func.now() - Session.created_at > lifetime)

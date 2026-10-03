from typing import Optional
from datetime import timedelta

from sqlalchemy import func

from dnevnikru import AioDnevnikruApi
from ...dependencies.httpx import get_httpx_client
from dnevnikru.exceptions import DnevnikruApiException

from ...models.teacher_session_model import TeacherSession
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['TeacherSessionRepository']


class TeacherSessionRepository(SqlAlchemyRepository[TeacherSession]):
    """Репозиторий для взаимодействия с сессиями пользователей"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, TeacherSession)

    async def create_teacher_session(self, session_id: str, teacher_id: int, dnevnik_token: str) -> Optional[TeacherSession]:
        """
        Создать сессию учителя

        :param session_id: идентификатор сессии
        :param teacher_id: идентификатор учителя
        :param dnevnik_token: API-токен Дневника.ру для взаимодействия с ним
        :return: созданная сессия
        """

        return await self.create({
            'session_id': session_id,
            'teacher_id': teacher_id,
            'dnevnik_token': dnevnik_token
        }, security=['session_id'], security_nothing=True)

    async def get_session(self, session_id: str, only_life: bool = True) -> Optional[TeacherSession]:
        """
        Получить сессию по идентификатору

        :param session_id: идентификатор сессии
        :param only_life: только работающие сессии с флагом life=true
        :return: сессия, если существует
        """

        return await self.get_single(
            TeacherSession.session_id == session_id,
            *((TeacherSession.life == True,) if only_life else ())
        )

    async def get_sessions(self, teacher_id: int) -> list[TeacherSession]:
        """
        Получить все работающие сессии учителя

        :param teacher_id: идентификатор учителя
        :return: список работающих сессий
        """

        return await self.get_multi(TeacherSession.teacher_id == teacher_id, TeacherSession.life == True)

    async def kill_session(self, session_id: str) -> Optional[TeacherSession]:
        """
        Пометить сессию как неработающую с флагом life=false

        :param session_id: идентификатор сессии
        :return: обновленная сессия, если существует
        """

        return await self.update({'life': False}, TeacherSession.session_id == session_id)

    async def check_session_auth(self, session_id: str, dnr: AioDnevnikruApi = None) -> bool:
        """
        Проверить авторизацию сессии учителя в Дневнике.ру

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

    async def kill_old_sessions(self, lifetime: timedelta) -> list[TeacherSession]:
        """
        Пометить старые сессии неработающими

        :param lifetime: время жизни сессии
        """

        return await self.update_many({'life': False}, func.now() - TeacherSession.created_at > lifetime)

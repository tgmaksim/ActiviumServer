from sqlalchemy.sql import tuple_

from ...repositories.db_queue import AsyncDBQueue
from ...models.hidden_extracurricular_activity_model import HiddenExtracurricularActivity

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['HiddenExtracurricularActivityRepository']


class HiddenExtracurricularActivityRepository(SqlAlchemyRepository[HiddenExtracurricularActivity]):
    """Репозиторий для работы со скрытыми внеурочными занятиями"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, HiddenExtracurricularActivity)

    async def hide_ea(self, session_id: str, child_id: int, subject: str, place: str) -> HiddenExtracurricularActivity:
        """
        Скрытие внеурочного занятия для профиля пользователя

        :param session_id: идентификатор сессии пользователя
        :param child_id: идентификатор профиля (ребенка)
        :param subject: название предмета внеурочного занятия
        :param place: место проведения (кабинет) внеурочного занятия
        :return: запись скрытия внуерчоного занятия для пользователя
        """

        return await self.create({
            'session_id': session_id,
            'child_id': child_id,
            'subject': subject,
            'place': place
        }, security=['session_id', 'child_id', 'subject', 'place'], security_nothing=True)

    async def get_hidden_ea(self, profiles: list[tuple[str, int]]) -> list[HiddenExtracurricularActivity]:
        """
        Поучение скрытых внеурочных занятий у профилей пользователей

        :param profiles: пары (session_id, child_id)
        :return: все записи о скрытых внеурочных занятиях данных профилей пользователей
        """

        return await self.get_multi(
            tuple_(HiddenExtracurricularActivity.session_id, HiddenExtracurricularActivity.child_id).in_(profiles)
        )

    async def unhide_ea(self, session_id: str, child_id: int):
        """
        Удаление записей о скрытии внеурочных занятий для профиля пользователя

        :param session_id: идентификатор сессии пользователя
        :param child_id: идентификатор профиля (ребенка)
        """

        return await self.delete(HiddenExtracurricularActivity.session_id == session_id, HiddenExtracurricularActivity.child_id == child_id)

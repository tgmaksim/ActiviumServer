from datetime import datetime

from sqlalchemy import func

from ...repositories.db_queue import AsyncDBQueue
from ...models.information_model import Information

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['InformationRepository']


class InformationRepository(SqlAlchemyRepository[Information]):
    """Репозиторий для взаимодействия с информационными оповещениями при открытии приложения"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Information)

    async def create_information(
            self,
            parent_id: int,
            type_: str,
            time: datetime,
            title: str,
            text: str
    ) -> Information:
        """
        Создание информационного оповещения для пользователя

        :param parent_id: идентификатор пользователя
        :param type_: тип (класс) информационного оповещения для дополнительной работы с ним
        :param time: необходимое время оповещения
        :param title: заголовок информационного оповещения
        :param text: текст информационного оповещения
        :return: созданное информационное оповещение
        """

        return await self.create({
            'parent_id': parent_id,
            'time': time,
            'type': type_,
            'title': title,
            'text': text
        })

    async def get_informations(self, parent_id: int) -> list[Information]:
        """
        Получение всех информационных оповещений для пользователя, которые доступны к показу

        :param parent_id: идентификатор пользователя
        :return: список информационных оповещений, которые доступны к показу
        """

        return await self.get_multi(Information.parent_id == parent_id, Information.time <= func.now())

    async def delete_informations(self, parent_id: int):
        """
        Удаление всех истекших информационных оповещений у пользователя

        :param parent_id: идентификатор пользователя
        """

        return await self.delete(Information.parent_id == parent_id, Information.time <= func.now())

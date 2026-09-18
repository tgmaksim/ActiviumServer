from typing import Optional, Any

from src.models.tgbot_callback_data_model import TgbotCallbackData

from src.repositories.db_queue import AsyncDBQueue
from src.repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['TgbotCallbackDataRepository']


class TgbotCallbackDataRepository(SqlAlchemyRepository[TgbotCallbackData]):
    """Репозиторий для хранения данных кнопок Telegram-бота"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, TgbotCallbackData)

    async def get_data(self, module: str, action: str, key: int) -> Optional[TgbotCallbackData]:
        """
        Получить полное действие кнопки

        :param module: модуль Telegram-бота
        :param action: действие, совершаемое кнопкой
        :param key: ключ к данным кнопки
        :return: полная информация о действии кнопки
        """

        return await self.get_single(
            TgbotCallbackData.module == module,
            TgbotCallbackData.action == action,
            TgbotCallbackData.key == key
        )

    async def create_data(self, module: str, action: str, data: dict[str, Any]) -> TgbotCallbackData:
        """
        Записать действие кнопки

        :param module: модуль Telegram-бота
        :param action: действие кнопки
        :param data: дополнительные параметры действия кнопки
        :return: запись действия кнопки
        """

        return await self.create({
            'module': module,
            'action': action,
            'data': data
        })

    async def create_many_data(self, module: str, action: str, datas: list[dict[str, Any]]) -> list[TgbotCallbackData]:
        """
        Записать действия кнопок

        :param module: модуль Telegram-бота
        :param action: действие кнопок
        :param datas: дополнительные параметры действия кнопок
        :return: записи действия кнопок
        """

        return await self.create_many([
            {
                'module': module,
                'action': action,
                'data': data
            }
            for data in datas
        ])

    async def delete_data(self, module: str, action: str, key: int):
        """
        Удалить запись о действии кнопки

        :param module: модуль Telegram-бота
        :param action: действие, совершаемое кнопкой
        :param key: ключ данных кнопки
        """

        return await self.delete(
            TgbotCallbackData.module == module,
            TgbotCallbackData.action == action,
            TgbotCallbackData.key == key
        )

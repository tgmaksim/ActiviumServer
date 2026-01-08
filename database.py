import orjson

from config import db_config

from typing import Union, Optional
from asyncpg import Pool, Record, create_pool
from datetime import date, time, datetime, timedelta


__all__ = ['Database']

type NumberType = Union[int, float]
type DatetimeType = Union[date, time, datetime, timedelta]
type JsonType = Union[dict[str, SqlType], list[SqlType]]
type SqlType = Union[NumberType, DatetimeType, JsonType, bool, bytes, str, None]


class Database:
    """"
    Класс для взаимодействия с Postgres базой данных

    Пример:

    >>> async def main():
    ...     await Database.init()
    ...     await Database.execute("INSERT INTO table VALUES ($1, $2)", "value1", "value2")
    ...     await Database.close()
    """

    pool: Optional[Pool] = None
    """Пул соединений для одновременных запросов"""

    @classmethod
    async def init(cls):
        """Инициализация пула соединений"""

        if cls.pool is None:
            cls.pool = await create_pool(**db_config)

    @classmethod
    async def close(cls):
        """Закрытие соединения с базой данных"""

        if cls.pool is not None:
            await cls.pool.close()
            cls.pool = None

    @classmethod
    async def execute(cls, sql: str, *params):
        """
        Выполняет SQL-запрос и ничего не возвращает

        :param sql: SQL-запрос
        :param params: дополнительные параметры запроса
        """

        await cls.pool.execute(sql, *params)

    @classmethod
    async def executemany(cls, sql: str, params: list[tuple]):
        """
        Выполняет SQL-запрос несколько раз и ничего не возвращает

        :param sql: SQL-запрос
        :param params: дополнительные параметры запроса
        """

        await cls.pool.executemany(sql, params)

    @classmethod
    async def fetch_all(cls, sql: str, *params) -> list[dict[str, SqlType]]:
        """
        Выполняет SQL-запрос и возвращает список строк

        :param sql: SQL-запрос
        :param params: дополнительные параметры запроса
        :return: список словарей со строковым ключом (название столбца) и объектами SQL-типа
        """

        return cls.deserialize(await cls.pool.fetch(sql, *params))

    @classmethod
    async def fetch_all_for_one(cls, sql: str, *params) -> list[Optional[SqlType]]:
        """
        Выполняет SQL-запрос и возвращает список из одного результата каждого запроса

        :param sql: SQL-запрос
        :param params: дополнительные параметры запроса
        :return: список из одного результата каждого запроса
        """

        return [cls.deserialize(line, one=True) for line in await cls.pool.fetch(sql, *params)]

    @classmethod
    async def fetch_row(cls, sql: str, *params) -> dict[str, SqlType]:
        """
        Выполняет SQL-запрос и возвращает одну строку ответа

        :param sql: SQL-запрос
        :param params: дополнительные параметры запроса
        :return: словарь со строковым ключом (название столбца) и объекта SQL-типа
        """

        return cls.deserialize(await cls.pool.fetchrow(sql, *params))

    @classmethod
    async def fetch_row_for_one(cls, sql: str, *params) -> Optional[SqlType]:
        """
        Выполняет SQL-запрос и возвращает один результат одной строки ответа

        :param sql: SQL-запрос
        :param params: дополнительные параметры запроса
        :return: объект SQL-типа
        """

        return cls.deserialize(await cls.pool.fetchrow(sql, *params), one=True)

    @classmethod
    def deserialize(cls, data, one: bool = False):
        """
        Десериализует данные в JSON-формат

        :param data: данные для десериализации
        :param one: True, если необходимо из списка/словаря длиной 1 вытащить единственное значение, иначе False
        """

        if isinstance(data, list):
            result = [cls.deserialize(item, one=False) for item in data]
        elif isinstance(data, Record):
            result = {key: cls.deserialize(data[key], one=False) for key in data.keys()}
        else:
            try:
                result = orjson.loads(data)  # Если строка JSON-формата, то десериализуем
            except (TypeError, orjson.JSONDecodeError):
                return data

        if not one:
            return result  # Возвращаем весь объект

        if isinstance(result, list):
            if len(result) > 1:
                raise ValueError("Количество объектов в списке больше одного")
            return result[0]

        if isinstance(result, dict):
            if len(result) > 1:
                raise ValueError("Количество объектов в словаре больше одного")
            return list(result.values())[0]

        return result  # Объект нелинейный, возвращаем его целым

    @classmethod
    def serialize(cls, data: JsonType) -> str:
        """Сериализует словарь или список в JSON-строку"""

        return orjson.dumps(data).decode()

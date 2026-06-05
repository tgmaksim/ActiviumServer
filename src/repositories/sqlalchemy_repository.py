from typing import Type, Optional, Union, Iterable

from .db_queue import AsyncDBQueue
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select, update, ColumnElement

from .base_repository import AbstractRepository, ModelType


__all__ = ['SqlAlchemyRepository']


class SqlAlchemyRepository(AbstractRepository[ModelType]):
    """Репозиторий для взаимодействия с БД через SQL"""

    def __init__(self, queue: AsyncDBQueue, model: Type[ModelType]):
        self.queue = queue
        self.model = model

    async def create(self, data: dict, security: list[str] = None, security_nothing = False) -> ModelType:
        """
        Добавление строки в таблицу

        :param data: данные модели
        :param security: список полей с индексом unique для обновления других данных в той же строке в случае конфликта
        :param security_nothing: в случае конфликта полей security ничего не делать
        :return: созданная модель с данными
        """

        statement = insert(self.model).values(**data)

        # В случае конфликта UNIQUE
        if security:
            if security_nothing:  # Пропустить
                statement = statement.on_conflict_do_nothing(index_elements=security)
            else:  # Обновить
                statement = statement.on_conflict_do_update(
                    index_elements=security,
                    set_={field: data[field] for field in data if field not in security}
                )

        # Вернуть новые записи и обновить ORM-кэш
        statement = statement.returning(self.model)
        statement = statement.execution_options(populate_existing=True)

        res = await self.queue.execute(statement)
        return res.scalar()

    async def create_many(self, data: Iterable[dict], security: list[str] = None, security_nothing = False) -> list[ModelType]:
        """
        Добавление нескольких строк в таблицу

        :param data: данные модели
        :param security: список полей с индексом unique для обновления других данных в той же строке в случае конфликта
        :param security_nothing: в случае конфликта полей security ничего не делать
        :return: созданные модели с данными
        """

        if not data:
            return []

        statement = insert(self.model).values(data)

        # В случае конфликта UNIQUE
        if security:
            if security_nothing:  # Пропустить
                statement = statement.on_conflict_do_nothing(index_elements=security)
            else:  # Обновить
                raise ValueError("Пока что данный параметр недоступен")

        # Вернуть новые записи и обновить ORM-кэш
        statement = statement.returning(self.model)
        statement = statement.execution_options(populate_existing=True)

        res = await self.queue.execute(statement)
        return list(res.scalars().all())

    async def update(self, data: dict, *where, **filters) -> Optional[ModelType]:
        """
        Обновление данных в таблице. Если под условие попадется несколько строк, возникнет ошибка

        :param data: обновленные данные
        :param where: фильтры через модели
        :param filters: примитивные фильтры
        :return: обновленная модель (единственная), если есть
        """

        statement = update(self.model).values(**data)

        if where:
            statement = statement.where(*where)
        if filters:
            statement = statement.filter_by(**filters)

        # Вернуть новые записи и обновить ORM-кэш
        statement = statement.returning(self.model)
        statement = statement.execution_options(populate_existing=True)

        res = await self.queue.execute(statement)
        return res.scalar_one_or_none()

    async def update_many(self, data: dict, *where, **filters) -> list[ModelType]:
        """
        Обновление нескольких данных в таблице

        :param data: обновленные данные
        :param where: фильтры через модели
        :param filters: примитивные фильтры
        :return: обновленные модели, если есть
        """

        statement = update(self.model).values(**data)

        if where:
            statement = statement.where(*where)
        if filters:
            statement = statement.filter_by(**filters)

        # Вернуть новые записи и обновить ORM-кэш
        statement = statement.returning(self.model)
        statement = statement.execution_options(populate_existing=True)

        res = await self.queue.execute(statement)
        return list(res.scalars().all())

    async def delete(self, *where, **filters) -> Optional[int]:
        """
        Удаление данных из таблицы

        :param where: фильтры через модели
        :param filters: примитивные фильтры
        :return: количество удаленных строк (если вернула БД)
        """

        statement = delete(self.model)

        if where:
            statement = statement.where(*where)
        if filters:
            statement = statement.filter_by(**filters)

        res = await self.queue.execute(statement)
        return res.rowcount

    async def get_single(self, *where, **filters) -> Optional[ModelType]:
        """
        Получение единственного экземпляра данных в таблице

        :param where: фильтры через модели
        :param filters: примитивные фильтры
        :return: модель с данными, если есть
        """

        statement = select(self.model)

        if where:
            statement = statement.where(*where)
        if filters:
            statement = statement.filter_by(**filters)

        res = await self.queue.execute(statement)
        return res.scalar_one_or_none()

    async def get_first(
            self,
            *where,
            orders_: Union[Iterable[ColumnElement], ColumnElement] = None,
            **filters
    ) -> Optional[ModelType]:
        """
        Получение первой модели с данными по фильтрам

        :param where: фильтры через модели
        :param filters: примитивные фильтры
        :param orders_: правила сортировки
        :return: модель с данными, если есть
        """

        statement = select(self.model).limit(1)

        if where:
            statement = statement.where(*where)
        if orders_ is not None:
            if not isinstance(orders_, Iterable):
                orders_ = [orders_]
            statement = statement.order_by(*orders_)
        if filters:
            statement = statement.filter_by(**filters)

        res = await self.queue.execute(statement)
        return res.scalar_one_or_none()

    async def get_multi(
            self,
            *where,
            orders_: Union[Iterable[ColumnElement], ColumnElement] = None,
            limit: int = None,
            offset: int = None,
            **filters
    ) -> list[ModelType]:
        """
        Получение нескольких моделей с данными по фильтрам

        :param where: фильтры через модели
        :param filters: примитивные фильтры
        :param orders_: правила сортировки
        :param limit: лимит количества
        :param offset: смещение списка
        :return: модели с данными
        """

        statement = select(self.model)

        if where:
            statement = statement.where(*where)
        if orders_ is not None:
            if not isinstance(orders_, Iterable):
                orders_ = [orders_]
            statement = statement.order_by(*orders_)
        if filters:
            statement = statement.filter_by(**filters)
        if limit is not None:
            statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)

        res = await self.queue.execute(statement)
        return list(res.scalars().all())

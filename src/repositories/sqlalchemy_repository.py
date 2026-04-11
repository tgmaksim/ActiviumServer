from typing import Type, Optional, Union, Iterable

from .db_queue import AsyncDBQueue
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select, update, ColumnElement

from .base_repository import AbstractRepository, ModelType


__all__ = ['SqlAlchemyRepository']


class SqlAlchemyRepository(AbstractRepository[ModelType]):
    def __init__(self, queue: AsyncDBQueue, model: Type[ModelType]):
        self.queue = queue
        self.model = model

    async def create(self, data: dict, security: list[str] = None, security_nothing = False) -> ModelType:
        statement = insert(self.model).values(**data)
        if security:
            if security_nothing:
                statement = statement.on_conflict_do_nothing(index_elements=security)
            else:
                statement = statement.on_conflict_do_update(
                    index_elements=security,
                    set_={field: data[field] for field in data if field not in security}
                )
        statement = statement.returning(self.model)
        res = await self.queue.execute(statement)
        return res.scalar()

    async def create_many(self, data: Iterable[dict]) -> list[ModelType]:
        statement = insert(self.model).values(*data)
        statement = statement.returning(self.model)
        res = await self.queue.execute(statement)
        return list(res.scalars().all())

    async def update(self, data: dict, *where, **filters) -> Optional[ModelType]:
        statement = update(self.model).values(**data)

        if where:
            statement = statement.where(*where)
        if filters:
            statement = statement.filter_by(**filters)

        statement = statement.returning(self.model)
        res = await self.queue.execute(statement)
        return res.scalar_one_or_none()

    async def delete(self, *where, **filters) -> Optional[int]:
        statement = delete(self.model)

        if where:
            statement = statement.where(*where)
        if filters:
            statement = statement.filter_by(**filters)

        res = await self.queue.execute(statement)
        return res.rowcount

    async def get_single(self, *where, **filters) -> Optional[ModelType]:
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

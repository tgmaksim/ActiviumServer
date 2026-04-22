from ...repositories.db_queue import AsyncDBQueue
from ...models.school_post_model import SchoolPost

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SchoolPostRepository']


class SchoolPostRepository(SqlAlchemyRepository[SchoolPost]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, SchoolPost)

from typing import Optional

from ...models.teacher_model import Teacher
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['TeacherRepository']


class TeacherRepository(SqlAlchemyRepository[Teacher]):
    """Репозиторий для взаимодействия с учителями"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Teacher)

    async def get_teacher(self, teacher_id: int) -> Optional[Teacher]:
        """
        Получения учителя по идентификатору

        :param teacher_id: идентификатор учителя
        :return: учитель, если существует
        """

        return await self.get_single(Teacher.teacher_id == teacher_id)

    async def create_teacher(self, teacher_id: int) -> Teacher:
        """
        Создание учителя

        :param teacher_id: идентификатор учителя, взятый из Дневника.ру как person_id
        :return: новый учитель
        """

        return await self.create({
            'teacher_id': teacher_id
        })

    async def get_teachers(self, teachers_id: list[int]) -> list[Teacher]:
        """
        Получение учителей по идентификаторам

        :param teachers_id: идентификаторы пользователей
        :return: найденные учителя
        """

        return await self.get_multi(Teacher.teacher_id.in_(teachers_id))

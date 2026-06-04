from typing import Optional
from datetime import timedelta, datetime

from sqlalchemy import func, select

from ...repositories.db_queue import AsyncDBQueue
from ...models.lesson_note_model import LessonNote

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['LessonNoteRepository']


class LessonNoteRepository(SqlAlchemyRepository[LessonNote]):
    """Репозиторий для работы с заметками к урокам у детей (профилей)"""

    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, LessonNote)

    async def create_note(
            self,
            child_id: int,
            lesson_id: int,
            text: str,
            public: bool,
            remind_time: Optional[datetime]
    ) -> LessonNote:
        """
        Создание заметки к уроку

        :param child_id: идентификатор ребенка (профиля)
        :param lesson_id: идентификатор урока, взятый из Дневника.ру
        :param text: текст заметки
        :param public: закрытые заметки доступны только ребенку (владельцу профиля)
        :param remind_time: время напоминания о заметке
        :return: созданная заметка к уроку
        """

        return await self.create({
            'child_id': child_id,
            'lesson_id': lesson_id,
            'text': text,
            'public': public,
            'remind_time': remind_time
        }, security=['child_id', 'lesson_id'])

    async def get_note(self, child_id: int, lesson_id: int) -> Optional[LessonNote]:
        """
        Получение заметки к уроку

        :param child_id: идентификатор ребенка (профиля)
        :param lesson_id: идентификатор урока, взятый из Дневника.ру
        :return: заметка к уроку, если существует
        """

        return await self.get_single(LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

    async def delete_note(self, child_id: int, lesson_id: int):
        """
        Удаление заметки к уроку

        :param child_id: идентификатор ребенка (профиля)
        :param lesson_id: идентификатор урока, взятый из Дневника.ру
        """

        return await self.delete(
            LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

    async def get_notes(self, child_id: int, lessons_id: list[int], only_public: bool = False) -> dict[int, LessonNote]:
        """
        Получение заметой к уроку

        :param child_id: идентификатор ребенка (профиля)
        :param lessons_id: идентификаторы уроков, взятых из Дневника.ру
        :param only_public: получить только открытые заметки, доступные не только ребенку (владельцу профиля)
        :return: заметки по идентификаторам уроков
        """

        notes = await self.get_multi(
            LessonNote.child_id == child_id,
            LessonNote.lesson_id.in_(lessons_id),
            *((LessonNote.public == True,) if only_public else ())
        )
        return {note.lesson_id: note for note in notes}

    async def delete_old_note(self, lifetime: timedelta):
        """
        Удаление старых заметок к урокам

        :param lifetime: время жизни заметок к урокам
        """

        return await self.delete(func.now() - LessonNote.created_at > lifetime)

    async def get_next_notes_to_remind(self, start_time_period: tuple[datetime, datetime]) -> list[LessonNote]:
        """
        Получение заметок к урокам для напоминания в течение периода.
        Используется skip_locked для правильной конкурентной работы нескольких worker'ов

        :param start_time_period: период, в течение которого установлено напоминание
        :return: список заметок к урокам для напоминания
        """

        # Получить все заметки к урокам, у которых remind_time принадлежит периоду
        statement = (
            select(LessonNote)
            .where(
                LessonNote.remind_time.is_not(None),
                LessonNote.remind_time.between(*start_time_period),
            )
            .order_by(LessonNote.remind_time)  # Сортировка по времени напоминания
            .with_for_update(skip_locked=True)
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()

    async def delete_note_remind(self, child_id: int, lesson_id: int) -> Optional[LessonNote]:
        """
        Удаление напоминания у заметки к уроку

        :param child_id: идентификатор ребенка (профиля)
        :param lesson_id: идентификатор урока, взятый из Дневника.ру
        :return: обновленная заметка к уроку, если такая существует
        """

        return await self.update({
            'remind_time': None
        }, LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

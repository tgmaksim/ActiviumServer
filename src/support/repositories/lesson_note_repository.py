from typing import Optional
from datetime import timedelta, datetime

from sqlalchemy import func, select

from ...repositories.db_queue import AsyncDBQueue
from ...models.lesson_note_model import LessonNote

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['LessonNoteRepository']


class LessonNoteRepository(SqlAlchemyRepository[LessonNote]):
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
        return await self.create({
            'child_id': child_id,
            'lesson_id': lesson_id,
            'text': text,
            'public': public,
            'remind_time': remind_time
        }, security=['child_id', 'lesson_id'])

    async def get_note(self, child_id: int, lesson_id: int) -> Optional[LessonNote]:
        return await self.get_single(LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

    async def delete_note(self, child_id: int, lesson_id: int):
        return await self.delete(
            LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

    async def get_notes(self, child_id: int, lessons_id: list[int], only_public: bool = False) -> dict[int, LessonNote]:
        if only_public:
            notes = await self.get_multi(
                LessonNote.child_id == child_id, LessonNote.lesson_id.in_(lessons_id), LessonNote.public == True)
        else:
            notes = await self.get_multi(LessonNote.child_id == child_id, LessonNote.lesson_id.in_(lessons_id))
        return {note.lesson_id: note for note in notes}

    async def delete_old_note(self, lifetime: timedelta):
        return await self.delete(func.now() - LessonNote.created_at > lifetime)

    async def get_next_notes_to_remind(self, start_time_period: tuple[datetime, datetime]) -> list[LessonNote]:
        statement = (
            select(LessonNote)
            .where(
                LessonNote.remind_time.is_not(None),
                LessonNote.remind_time.between(*start_time_period),
            )
            .order_by(LessonNote.remind_time)
            .with_for_update(skip_locked=True)
        )

        res = await self.queue.execute(statement)
        return res.scalars().all()

    async def delete_note_remind(self, child_id: int, lesson_id: int):
        return await self.update({
            'remind_time': None
        }, LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

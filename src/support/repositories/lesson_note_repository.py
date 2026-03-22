from typing import Optional

from ...repositories.db_queue import AsyncDBQueue
from ...models.lesson_note_model import LessonNote

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['LessonNoteRepository']


class LessonNoteRepository(SqlAlchemyRepository[LessonNote]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, LessonNote)

    async def create_note(self, child_id: int, lesson_id: int, text: str) -> LessonNote:
        return await self.create({
            'child_id': child_id,
            'lesson_id': lesson_id,
            'text': text
        }, security=['child_id', 'lesson_id'])

    async def get_note(self, child_id: int, lesson_id: int) -> Optional[LessonNote]:
        return await self.get_single(LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

    async def delete_note(self, child_id: int, lesson_id: int):
        return await self.delete(LessonNote.child_id == child_id, LessonNote.lesson_id == lesson_id)

    async def get_notes(self, child_id: int, lessons_id: list[int]) -> dict[int, LessonNote]:
        notes = await self.get_multi(LessonNote.child_id == child_id, LessonNote.lesson_id.in_(lessons_id))
        return {note.lesson_id: note for note in notes}

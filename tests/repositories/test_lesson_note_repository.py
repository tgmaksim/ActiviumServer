import pytest

from datetime import datetime, UTC, timedelta

from sqlalchemy.exc import IntegrityError

from src.models.child_model import Child

from src.support.repositories.child_repository import ChildRepository
from src.support.repositories.lesson_note_repository import LessonNoteRepository


@pytest.mark.asyncio
async def test_create_note(
    lesson_note_repository: LessonNoteRepository,
    child
):
    remind_time = datetime(
        2028, 1, 10, 12, 0,
        tzinfo=UTC
    )

    result = await lesson_note_repository.create_note(
        child_id=child.child_id,
        lesson_id=1000,
        text="Homework",
        public=True,
        remind_time=remind_time
    )

    assert result is not None

    assert result.child_id == child.child_id
    assert result.lesson_id == 1000
    assert result.text == "Homework"
    assert result.public is True
    assert result.remind_time == remind_time


@pytest.mark.asyncio
async def test_create_note_updates_existing(
    lesson_note_repository: LessonNoteRepository,
    lesson_note,
    child
):
    result = await lesson_note_repository.create_note(
        child_id=child.child_id,
        lesson_id=lesson_note.lesson_id,
        text="Updated text",
        public=False,
        remind_time=None
    )

    assert result.text == "Updated text"
    assert result.public is False
    assert result.remind_time is None

    notes = await lesson_note_repository.get_multi()

    assert len(notes) == 1


@pytest.mark.asyncio
async def test_get_note(
    lesson_note_repository: LessonNoteRepository,
    lesson_note,
    child
):
    result = await lesson_note_repository.get_note(
        child.child_id,
        lesson_note.lesson_id
    )

    assert result is not None

    assert result.lesson_id == lesson_note.lesson_id


@pytest.mark.asyncio
async def test_get_unknown_note_returns_none(
    lesson_note_repository: LessonNoteRepository,
    child
):
    result = await lesson_note_repository.get_note(
        child.child_id,
        999999
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_note(
    lesson_note_repository: LessonNoteRepository,
    lesson_note,
    child
):
    await lesson_note_repository.delete_note(
        child.child_id,
        lesson_note.lesson_id
    )

    result = await lesson_note_repository.get_note(
        child.child_id,
        lesson_note.lesson_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_notes(
    lesson_note_repository: LessonNoteRepository,
    lesson_notes,
    child
):
    result = await lesson_note_repository.get_notes(
        child.child_id,
        [1000, 1001, 1002]
    )

    assert len(result) == 3

    assert 1000 in result
    assert 1001 in result
    assert 1002 in result

    assert result[1000].text == "Public note"


@pytest.mark.asyncio
async def test_get_public_notes_only(
    lesson_note_repository: LessonNoteRepository,
    lesson_notes,
    child
):
    result = await lesson_note_repository.get_notes(
        child.child_id,
        [1000, 1001, 1002],
        only_public=True
    )

    assert len(result) == 2

    assert 1000 in result
    assert 1002 in result

    assert 1001 not in result


@pytest.mark.asyncio
async def test_get_next_notes_to_remind(
    lesson_note_repository: LessonNoteRepository,
    lesson_notes
):
    result = await lesson_note_repository.get_next_notes_to_remind((
        datetime(
            2028, 1, 10, 11, 0,
            tzinfo=UTC
        ),
        datetime(
            2028, 1, 10, 12, 30,
            tzinfo=UTC
        )
    ))

    assert len(result) == 1

    assert result[0].lesson_id == 1000


@pytest.mark.asyncio
async def test_get_next_notes_to_remind_ignores_null(
    lesson_note_repository: LessonNoteRepository,
    lesson_notes
):
    result = await lesson_note_repository.get_next_notes_to_remind((
        datetime(
            2028, 1, 10, 11, 0,
            tzinfo=UTC
        ),
        datetime(
            2028, 1, 10, 14, 0,
            tzinfo=UTC
        )
    ))

    lesson_ids = [note.lesson_id for note in result]

    assert 1001 not in lesson_ids


@pytest.mark.asyncio
async def test_delete_note_remind(
    lesson_note_repository: LessonNoteRepository,
    lesson_note,
    child
):
    await lesson_note_repository.delete_note_remind(
        child.child_id,
        lesson_note.lesson_id
    )

    result = await lesson_note_repository.get_note(
        child.child_id,
        lesson_note.lesson_id
    )

    assert result.remind_time is None


@pytest.mark.asyncio
async def test_delete_old_note(
    lesson_note_repository: LessonNoteRepository,
    lesson_note
):
    await lesson_note_repository.delete_old_note(
        timedelta(days=-1)
    )

    result = await lesson_note_repository.get_multi()

    assert result == []


@pytest.mark.asyncio
async def test_create_note_unknown_child_raises_error(
    lesson_note_repository: LessonNoteRepository
):
    with pytest.raises(IntegrityError):
        await lesson_note_repository.create_note(
            child_id=999999,
            lesson_id=1000,
            text="Test",
            public=True,
            remind_time=None
        )


@pytest.mark.asyncio
async def test_delete_child_cascades_notes(
    child_repository: ChildRepository,
    lesson_note_repository: LessonNoteRepository,
    lesson_note,
    child
):
    await child_repository.delete(
        Child.child_id == child.child_id
    )

    result = await lesson_note_repository.get_multi()

    assert result == []

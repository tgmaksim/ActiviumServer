from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Note', 'CreateNoteResult', 'CreateNoteApiResponse', 'NoteResult', 'NoteApiResponse', 'DeleteNoteApiResponse',
           'PraiseApiResponse']


class Note(ApiBase):
    classId: ClassVar[int] = 0x34
    class_id: Literal[0x34] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    lessonKey: str = Field(
        description="Ключ к уроку, к которому создана заметка"
    )
    text: str = Field(
        description="Текст заметки"
    )
    public: bool = Field(
        description="Заметка доступна родителю"
    )


class CreateNoteResult(ApiBase):
    classId: ClassVar[int] = 0x35
    class_id: Literal[0x35] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    note: Note = Field(
        description="Созданная заметка к уроку"
    )


class CreateNoteApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x36
    class_id: Literal[0x36, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[CreateNoteResult] = Field(
        default=None,
        description="Созданная заметка"
    )


class NoteResult(ApiBase):
    classId: ClassVar[int] = 0x37
    class_id: Literal[0x37] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    note: Optional[Note] = Field(
        description="Заметка к уроку, если есть"
    )


class NoteApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x38
    class_id: Literal[0x38, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[NoteResult] = Field(
        default=None,
        description="Заметка к уроку"
    )


class DeleteNoteApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x39
    class_id: Literal[0x39, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class PraiseApiResponse(ApiResponse):
    classId: ClassVar[int] = 0x3A
    class_id: Literal[0x3A, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )

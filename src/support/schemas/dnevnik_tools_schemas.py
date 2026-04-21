from datetime import datetime
from typing import ClassVar, Literal, Optional

from pydantic import Field

from ...schemas.base_schema import ApiBase
from ...schemas.response_schema import ApiResponse


__all__ = ['Note0x34', 'CreateNoteApiResponse0x36', 'NoteResult0x35', 'NoteApiResponse0x38', 'DeleteNoteApiResponse',
           'PraiseApiResponse0x3A', 'HighlightPersonApiResponse', 'UnhighlightPersonApiResponse', 'PraiseApiResponse',
           'Note', 'CreateNoteApiResponse', 'NoteResult', 'NoteApiResponse']


class Note0x34(ApiBase):  # До версии API 1.4.1
    """Заметка"""

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


class Note(ApiBase):  # Начиная с версии API 1.5.0
    """Заметка"""

    classId: ClassVar[int] = 0x4A
    class_id: Literal[0x4A] = Field(
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
    remindTime: Optional[datetime] = Field(
        description="Время напоминания, если установлено"
    )


class NoteResult0x35(ApiBase):  # До версии API 1.4.1
    """Результат запроса создания или получения заметки к уроку"""

    classId: ClassVar[int] = 0x35
    class_id: Literal[0x35] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    note: Optional[Note0x34] = Field(
        description="Заметка к уроку, если есть"
    )


class NoteResult(ApiBase):   # Начиная с версии API 1.5.0
    """Результат запроса создания или получения заметки к уроку"""

    classId: ClassVar[int] = 0x4B
    class_id: Literal[0x4B] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    note: Optional[Note] = Field(
        description="Заметка к уроку, если есть"
    )


class CreateNoteApiResponse0x36(ApiResponse):  # До версии API 1.4.1
    """Ответ на запрос создания заметки к уроку"""

    classId: ClassVar[int] = 0x36
    class_id: Literal[0x36, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[NoteResult0x35] = Field(
        default=None,
        description="Созданная заметка"
    )


class CreateNoteApiResponse(ApiResponse):  # Начиная с версии API 1.5.0
    """Ответ на запрос создания заметки к уроку"""

    classId: ClassVar[int] = 0x4C
    class_id: Literal[0x4C, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[NoteResult] = Field(
        default=None,
        description="Созданная заметка"
    )


class NoteApiResponse0x38(ApiResponse):  # До версии API 1.4.1
    """Ответ на запрос получения заметки к уроку"""

    classId: ClassVar[int] = 0x38
    class_id: Literal[0x38, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[NoteResult0x35] = Field(
        default=None,
        description="Заметка к уроку"
    )


class NoteApiResponse(ApiResponse):  # Начиная с версии API 1.5.0
    """Ответ на запрос получения заметки к уроку"""

    classId: ClassVar[int] = 0x4D
    class_id: Literal[0x4D, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: Optional[NoteResult] = Field(
        default=None,
        description="Заметка к уроку"
    )


class DeleteNoteApiResponse(ApiResponse):
    """Ответ на запрос удаления заметки к уроку"""

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


class PraiseApiResponse0x3A(ApiResponse):
    """Ответ на запрос отправки похвалы"""

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


class PraiseApiResponse(ApiResponse):
    """Ответ на запрос отправки похвалы"""

    classId: ClassVar[int] = 0x49
    class_id: Literal[0x49, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class HighlightPersonApiResponse(ApiResponse):
    """Ответ на запрос выделения одноклассника в рейтингах"""

    classId: ClassVar[int] = 0x3E
    class_id: Literal[0x3E, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )


class UnhighlightPersonApiResponse(ApiResponse):
    """Ответ на запрос отмены выделения одноклассника в рейтингах"""

    classId: ClassVar[int] = 0x3F
    class_id: Literal[0x3F, 0x2] = Field(
        default=classId,
        alias='classId',
        description="Идентификатор класса"
    )

    answer: None = Field(
        default=None,
        description="Всегда null"
    )

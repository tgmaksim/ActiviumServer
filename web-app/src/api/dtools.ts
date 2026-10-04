import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";

/**
 * Заметка к уроку.
 *
 * @property lessonKey Ключ урока, к которому создана заметка.
 * @property text Текст заметки.
 * @property public Заметка доступна родителю.
 * @property remindTime Время напоминания или null.
 */
export interface Note extends ApiBase {
    classId: 0x4A;
    lessonKey: string;
    text: string;
    public: boolean;
    remindTime: string | null;
}

/**
 * Результат запроса создания или получения заметки к уроку.
 *
 * @property note Созданная или полученная заметка.
 */
export interface NoteResult extends ApiBase {
    classId: 0x4B;
    note: Note | null;
}

/**
 * Ответ на запрос создания заметки к уроку.
 */
export interface CreateNoteApiResponse
    extends ApiResponse<NoteResult | null> {
    classId: 0x4C | 0x2;
}

/**
 * Ответ на запрос получения заметки к уроку.
 */
export interface NoteApiResponse
    extends ApiResponse<NoteResult | null> {
    classId: 0x4D | 0x2;
}

/**
 * Ответ на запрос удаления заметки к уроку.
 *
 * answer всегда равен null.
 */
export interface DeleteNoteApiResponse
    extends ApiResponse<null> {
    classId: 0x39 | 0x2;
}

/**
 * Ответ на запрос отправки похвалы.
 *
 * answer всегда равен null.
 */
export interface PraiseApiResponse
    extends ApiResponse<null> {
    classId: 0x49 | 0x2;
}

/**
 * Ответ на запрос выделения одноклассника в рейтингах.
 *
 * answer всегда равен null.
 */
export interface HighlightPersonApiResponse
    extends ApiResponse<null> {
    classId: 0x3E | 0x2;
}

/**
 * Ответ на запрос отмены выделения одноклассника в рейтингах.
 *
 * answer всегда равен null.
 */
export interface UnhighlightPersonApiResponse
    extends ApiResponse<null> {
    classId: 0x3F | 0x2;
}


const PATH_PREFIX = "dtools";

const PATH_CREATE_NOTE = "createNote";
const PATH_GET_NOTE = "getNote";
const PATH_DELETE_NOTE = "deleteNote";
const PATH_SEND_PRAISE = "sendPraise";
const PATH_HIGHLIGHT_PERSON = "highlightPerson";
const PATH_UNHIGHLIGHT_PERSON = "unhighlightPerson";

const CREATE_NOTE_VERSION = 1;
const GET_NOTE_VERSION = 1;
const DELETE_NOTE_VERSION = 0;
const SEND_PRAISE_VERSION = 1;
const HIGHLIGHT_PERSON_VERSION = 0;
const UNHIGHLIGHT_PERSON_VERSION = 0;


/**
 * Создание или изменение текстовой заметки к уроку.
 *
 * Заметка синхронизируется с родителем.
 *
 * @param lessonKey Ключ урока.
 * @param text Текст заметки.
 * @param public Доступна ли заметка родителю.
 * @param remindTime Время напоминания или null.
 */
async function createNote(
    lessonKey: string,
    text: string,
    public_: boolean,
    remindTime: string | null,
): Promise<CreateNoteApiResponse> {
    const params: Record<
        string,
        string | number | boolean
    > = {
        lessonKey,
        public: public_,
    };

    if (remindTime !== null) {
        params.remindTime = remindTime;
    }

    return Request.post<CreateNoteApiResponse>(
        [
            PATH_PREFIX,
            PATH_CREATE_NOTE,
            CREATE_NOTE_VERSION,
        ].join("/"),
        params,
        text,
    );
}


/**
 * Получение текстовой заметки к уроку.
 *
 * @param lessonKey Ключ урока.
 */
async function getNote(
    lessonKey: string,
): Promise<NoteApiResponse> {
    return Request.get<NoteApiResponse>(
        [
            PATH_PREFIX,
            PATH_GET_NOTE,
            GET_NOTE_VERSION,
        ].join("/"),
        {
            lessonKey,
        },
    );
}


/**
 * Удаление текстовой заметки к уроку.
 *
 * @param lessonKey Ключ урока.
 */
async function deleteNote(
    lessonKey: string,
): Promise<DeleteNoteApiResponse> {
    return Request.delete<DeleteNoteApiResponse>(
        [
            PATH_PREFIX,
            PATH_DELETE_NOTE,
            DELETE_NOTE_VERSION,
        ].join("/"),
        {
            lessonKey,
        },
    );
}


/**
 * Отправка похвалы активному ребенку от родителя
 * на полученные оценки.
 *
 * Если передан lessonKey, похвала отправляется
 * для конкретного урока. Иначе используется ratingKey.
 *
 * @param lessonKey Ключ урока или null.
 * @param ratingKey Ключ оценки или null.
 * @param text Текст похвалы или null.
 */
async function sendPraise(
    lessonKey: string | null,
    ratingKey: string | null,
    text: string | null,
): Promise<PraiseApiResponse> {
    const params =
        lessonKey !== null
            ? { lessonKey }
            : { ratingKey: ratingKey! };

    return Request.post<PraiseApiResponse>(
        [
            PATH_PREFIX,
            PATH_SEND_PRAISE,
            SEND_PRAISE_VERSION,
        ].join("/"),
        params,
        text,
    );
}


/**
 * Выделение одноклассника во всех рейтингах
 * и списках других оценок.
 *
 * @param personKey Ключ ученика.
 */
async function highlightPerson(
    personKey: string,
): Promise<HighlightPersonApiResponse> {
    return Request.put<HighlightPersonApiResponse>(
        [
            PATH_PREFIX,
            PATH_HIGHLIGHT_PERSON,
            HIGHLIGHT_PERSON_VERSION,
        ].join("/"),
        {
            personKey,
        },
    );
}


/**
 * Отмена ранее включенного выделения одноклассника
 * в рейтингах.
 *
 * @param personKey Ключ ученика.
 */
async function unhighlightPerson(
    personKey: string,
): Promise<UnhighlightPersonApiResponse> {
    return Request.put<UnhighlightPersonApiResponse>(
        [
            PATH_PREFIX,
            PATH_UNHIGHLIGHT_PERSON,
            UNHIGHLIGHT_PERSON_VERSION,
        ].join("/"),
        {
            personKey,
        },
    );
}


/**
 * API-запросы группы dtools.
 */
export const DnevnikTools = {
    createNote,
    getNote,
    deleteNote,
    sendPraise,
    highlightPerson,
    unhighlightPerson,
};

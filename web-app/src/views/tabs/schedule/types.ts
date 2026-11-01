/**
 * Календарная дата в формате YYYY-MM-DD.
 */
export type ScheduleDate = string;

export interface UiScheduleResult {
    schedule: (UiScheduleDay | null)[];
    timezone: number;
    hasAbilityPraise: boolean;
}

export interface UiScheduleDay {
    date: string;
    lessons: UiScheduleLesson[];
    ea: ScheduleDay["ea"];
    schoolPosts: SchoolPost[];
}

export interface UiScheduleLesson {
    lessonKey: string | null;
    number: number;
    subject: string;
    place: string;
    hours: ScheduleLesson["hours"];
    works: ScheduleLesson["works"];
    logs: ScheduleLesson["logs"];
    othersMarks: ScheduleLesson["othersMarks"];
    avgGroupLessonMark: ScheduleLesson["avgGroupLessonMark"];
    homework: string | null;
    note: Note | null;
    files: ScheduleLesson["files"];
    ratingKey: string | null;
    dnevnikruUrl: string | null;
    praiseState: LoadState<never> | null;
    noteState: LoadState<NoteResult> | null;
    isExtra: boolean;
}

/**
 * День для отображения в горизонтальном Pager.
 *
 * data === null означает, что данные для дня ещё не получены.
 * Это не выходной день.
 */
export interface SchedulePagerDay {
    date: ScheduleDate;
    data: UiScheduleDay | null;
}

/**
 * Алиасы для совместимости с существующими компонентами.
 */
export type ScheduleDay = UiScheduleDay;
export type ScheduleLesson = UiScheduleLesson;
import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";
import type { Note } from "./dtools";
import type { SchoolPost } from "./school";

/**
 * Прикрепленный файл к домашнему заданию.
 */
export interface ScheduleHomeworkDocument extends ApiBase {
    classId: 0xA;
    fileName: string;
    downloadUrl: string;
}

/**
 * Время проведения урока или внеурочного занятия.
 */
export interface ScheduleHours extends ApiBase {
    classId: 0xB;
    start: string;
    end: string;
    string: string;
}

/**
 * Внеурочное занятие.
 */
export interface ScheduleExtracurricularActivity extends ApiBase {
    classId: 0xC;
    subject: string;
    place: string;
    hours: ScheduleHours;
}

/**
 * Тип работы на уроке.
 */
export interface WorkType extends ApiBase {
    classId: 0xD;
    title: string;
    abbr: string;
}

/**
 * Оценка или отметка посещаемости урока.
 */
export interface MarkLog extends ApiBase {
    classId: 0xE;
    mood: string;
    value: string;
    work: WorkType | null;
    created: string | null;
    ratingKey: string | null;
}

/**
 * Оценки другого ученика(цы) за тот же урок.
 */
export interface MarksOther extends ApiBase {
    classId: 0xF;
    number: number | null;
    name: string;
    personKey: string | null;
    isHighlighting: boolean | null;
    marks: MarkLog[];
}

/**
 * Урок.
 */
export interface ScheduleLesson extends ApiBase {
    classId: 0x5B;
    lessonKey: string;
    number: number;
    subject: string;
    place: string;
    hours: ScheduleHours;
    works: WorkType[];
    logs: MarkLog[];
    othersMarks: MarksOther[];
    avgGroupLessonMark: MarkLog | null;
    homework: string | null;
    note: Note | null;
    files: ScheduleHomeworkDocument[];
    ratingKey: string | null;
    dnevnikruUrl: string;
}

/**
 * День в расписании с уроками и внеурочными занятиями.
 */
export interface ScheduleDay extends ApiBase {
    classId: 0x5C;
    date: string;
    lessons: ScheduleLesson[];
    ea: ScheduleExtracurricularActivity[];
    schoolPosts: SchoolPost[];
}

/**
 * Результат запроса расписания на несколько дней.
 */
export interface ScheduleResult extends ApiBase {
    classId: 0x5D;
    schedule: ScheduleDay[];
    timezone: number;
    hasAbilityPraise: boolean;
}

/**
 * Ответ на запрос расписания.
 */
export interface ScheduleApiResponse
    extends ApiResponse<ScheduleResult | null> {
    classId: 0x5E | 0x2;
}

/**
 * Результат запроса дополнительной статистики
 * по оценкам на уроке.
 */
export interface LessonRatingStatsResult extends ApiBase {
    classId: 0x14;
    oldAvgMark: MarkLog | null;
    newAvgMark: MarkLog | null;
}

/**
 * Ответ на запрос дополнительной статистики
 * по оценкам на уроке.
 */
export interface LessonRatingStatsApiResponse
    extends ApiResponse<LessonRatingStatsResult | null> {
    classId: 0x15 | 0x2;
}

/**
 * Последняя оценка.
 */
export interface MarkLast extends ApiBase {
    classId: 0x16;
    mark: MarkLog;
    subject: string;
    lessonDate: string | null;
    humanLessonDate: string | null;
    ratingKey: string;
}

/**
 * Оценки по предмету в отчетном периоде.
 */
export interface MarksSubjectPeriod extends ApiBase {
    classId: 0x17;
    subject: string;
    marks: MarkLog[];
    averageMark: MarkLog | null;
    periodMark: MarkLog | null;
    ratingKey: string;
}

/**
 * Результат запроса последних оценок
 * и оценок по предметам.
 */
export interface MarksResult extends ApiBase {
    classId: 0x18;
    recentMarks: MarkLast[];
    periodMarks: MarksSubjectPeriod[];
    ratingKey: string;
}

/**
 * Ответ на запрос последних оценок
 * и оценок по предметам.
 */
export interface MarksApiResponse
    extends ApiResponse<MarksResult | null> {
    classId: 0x19 | 0x2;
}

/**
 * Результат дополнительной статистики
 * по последней оценке.
 */
export interface MarksRatingStatsResult extends ApiBase {
    classId: 0x47;
    othersMarks: MarksOther[];
    avgGroupMark: MarkLog | null;
    oldAvgMark: MarkLog | null;
    newAvgMark: MarkLog | null;
    hasAbilityPraise: boolean;
}

/**
 * Ответ на дополнительную статистику
 * по последней оценке.
 */
export interface MarksRatingStatsApiResponse
    extends ApiResponse<MarksRatingStatsResult | null> {
    classId: 0x48 | 0x2;
}

/**
 * Результат общего или предметного рейтинга.
 */
export interface MarksSubjectRatingResult extends ApiBase {
    classId: 0x1C;
    rating: MarksOther[];
    oldMark: MarksOther | null;
}

/**
 * Ответ на общий или предметный рейтинг.
 */
export interface MarksSubjectRatingApiResponse
    extends ApiResponse<MarksSubjectRatingResult | null> {
    classId: 0x1D | 0x2;
}

/**
 * Оценки по предмету за отчетные периоды и за год.
 */
export interface MarksSubjectFinal extends ApiBase {
    classId: 0x1E;
    subject: string;
    marks: (MarkLog | null)[];
    finalMark: MarkLog | null;
}

/**
 * Результат оценок за отчетные периоды и за год.
 */
export interface MarksFinalResult extends ApiBase {
    classId: 0x1F;
    countPeriods: number;
    finalMarks: MarksSubjectFinal[];
}

/**
 * Ответ на оценки за отчетные периоды и за год.
 */
export interface MarksFinalApiResponse
    extends ApiResponse<MarksFinalResult | null> {
    classId: 0x20 | 0x2;
}

const PATH_PREFIX = "dnevnik";

const PATH_SCHEDULE = "getSchedule";
const PATH_LESSON_RATING_STATS = "getLessonRatingStats";
const PATH_MARKS = "getMarks";
const PATH_MARK_RATING_STATS = "getMarkRatingStats";
const PATH_MARKS_SUBJECT_RATING = "getMarksSubjectRating";
const PATH_FINAL_MARKS = "getFinalMarks";

const SCHEDULE_VERSION = 1;
const LESSON_RATING_STATS_VERSION = 0;
const MARKS_VERSION = 0;
const MARK_RATING_STATS_VERSION = 1;
const MARKS_SUBJECT_RATING_VERSION = 0;
const FINAL_MARKS_VERSION = 0;

/**
 * Получает расписание на несколько дней с домашними заданиями,
 * внеурочными занятиями и оценками с отметками о посещаемости.
 *
 * @param before Количество дней до сегодняшнего дня.
 * @param after Количество дней после сегодняшнего дня.
 */
async function getSchedule(
    before: number,
    after: number,
): Promise<ScheduleApiResponse> {
    return Request.get<ScheduleApiResponse>(
        [
            PATH_PREFIX,
            PATH_SCHEDULE,
            SCHEDULE_VERSION,
        ].join("/"),
        {
            before,
            after,
        },
    );
}

/**
 * Получает дополнительную статистику
 * по оценкам за урок.
 *
 * @param ratingKey Ключ урока.
 */
async function getLessonRatingStats(
    ratingKey: string,
): Promise<LessonRatingStatsApiResponse> {
    return Request.get<LessonRatingStatsApiResponse>(
        [
            PATH_PREFIX,
            PATH_LESSON_RATING_STATS,
            LESSON_RATING_STATS_VERSION,
        ].join("/"),
        {
            ratingKey,
        },
    );
}

/**
 * Получает последние оценки по дате выставления
 * и оценки за текущий отчетный период.
 *
 * @param last Количество дней для получения последних оценок.
 */
async function getMarks(
    last: number,
): Promise<MarksApiResponse> {
    return Request.get<MarksApiResponse>(
        [
            PATH_PREFIX,
            PATH_MARKS,
            MARKS_VERSION,
        ].join("/"),
        {
            last,
        },
    );
}

/**
 * Получает оценки класса за урок
 * и дополнительную статистику по полученной оценке.
 *
 * @param ratingKey Ключ последней оценки.
 */
async function getMarksRatingStats(
    ratingKey: string,
): Promise<MarksRatingStatsApiResponse> {
    return Request.get<MarksRatingStatsApiResponse>(
        [
            PATH_PREFIX,
            PATH_MARK_RATING_STATS,
            MARK_RATING_STATS_VERSION,
        ].join("/"),
        {
            ratingKey,
        },
    );
}

/**
 * Получает общий или предметный рейтинг класса.
 *
 * @param ratingKey Ключ предмета или общий ключ.
 */
async function getMarksSubjectRating(
    ratingKey: string,
): Promise<MarksSubjectRatingApiResponse> {
    return Request.get<MarksSubjectRatingApiResponse>(
        [
            PATH_PREFIX,
            PATH_MARKS_SUBJECT_RATING,
            MARKS_SUBJECT_RATING_VERSION,
        ].join("/"),
        {
            ratingKey,
        },
    );
}

/**
 * Получает оценки за отчетный период
 * и итоговые оценки за год.
 */
async function getFinalMarks(): Promise<MarksFinalApiResponse> {
    return Request.get<MarksFinalApiResponse>(
        [
            PATH_PREFIX,
            PATH_FINAL_MARKS,
            FINAL_MARKS_VERSION,
        ].join("/"),
    );
}

export const Dnevnik = {
    getSchedule,
    getLessonRatingStats,
    getMarks,
    getMarksRatingStats,
    getMarksSubjectRating,
    getFinalMarks,
};

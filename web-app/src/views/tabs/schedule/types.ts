import type {
    UiScheduleDay,
    UiScheduleLesson,
} from "./schedule-view-model";

/**
 * Календарная дата в формате YYYY-MM-DD.
 */
export type ScheduleDate = string;

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

export type {
    UiScheduleDay,
    UiScheduleLesson,
};
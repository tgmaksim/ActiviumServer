import type { ScheduleDate } from "./types";

/**
 * Преобразует timestamp в календарную дату
 * с учётом указанного смещения часового пояса.
 *
 * offsetSeconds — смещение относительно UTC в секундах.
 */
export function getCurrentDateInTimezone(
    offsetSeconds: number,
    timestamp: number = Date.now(),
): ScheduleDate {
    const date = new Date(timestamp + offsetSeconds * 1000);

    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

/**
 * Возвращает час в указанном часовом поясе.
 */
export function getCurrentHourInTimezone(
    offsetSeconds: number,
    timestamp: number = Date.now(),
): number {
    const date = new Date(timestamp + offsetSeconds * 1000);

    return date.getUTCHours();
}

/**
 * Прибавляет или вычитает календарные дни.
 *
 * Операция выполняется через UTC, поэтому не зависит
 * от переходов на летнее/зимнее время.
 */
export function addDays(
    date: ScheduleDate,
    days: number,
): ScheduleDate {
    const [year, month, day] = date.split("-").map(Number);

    const result = new Date(
        Date.UTC(year, month - 1, day + days),
    );

    const resultYear = result.getUTCFullYear();
    const resultMonth = String(
        result.getUTCMonth() + 1,
    ).padStart(2, "0");
    const resultDay = String(
        result.getUTCDate(),
    ).padStart(2, "0");

    return `${resultYear}-${resultMonth}-${resultDay}`;
}

/**
 * Формирует диапазон дат относительно сегодняшнего дня.
 */
export function buildDateRange(
    today: ScheduleDate,
    before: number,
    after: number,
): ScheduleDate[] {
    const firstDate = addDays(today, -before);

    return Array.from(
        { length: before + 1 + after },
        (_, index) => addDays(firstDate, index),
    );
}

/**
 * Определяет дату, которую нужно открыть при запуске.
 *
 * Если сейчас 15:00 или позднее, открываем следующий день.
 */
export function getDefaultScheduleDate(
    today: ScheduleDate,
    currentHour: number,
): ScheduleDate {
    return currentHour >= 15
        ? addDays(today, 1)
        : today;
}

/**
 * Проверяет корректность календарной даты.
 */
export function isScheduleDate(
    value: string,
): boolean {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        return false;
    }

    const [year, month, day] = value.split("-").map(Number);

    const date = new Date(Date.UTC(year, month - 1, day));

    return (
        date.getUTCFullYear() === year &&
        date.getUTCMonth() === month - 1 &&
        date.getUTCDate() === day
    );
}
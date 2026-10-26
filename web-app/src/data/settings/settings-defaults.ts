export const settingsDefaults = {
    installPromptHiddenKey: false,
    activeChildId: -1,
    darkTheme: false,
    beforeSchedule: 3,
    afterSchedule: 3,
    lastMarksPeriod: 5,
    showNullSubjectMarks: false,
    studyLessonMenu: false,
    studyMarkRating: false,
    studySubjectRating: false,
} as const;

/**
 * Время в Unix timestamp, секунды.
 */
export function getDefaultLastStudy(): string {
    return Math.floor(Date.now() / 1000).toString();
}
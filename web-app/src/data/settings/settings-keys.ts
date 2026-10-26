const SETTINGS_PREFIX = "activium:settings:";

export const settingsKeys = {
    installPromptHiddenKey: `${SETTINGS_PREFIX}installPromptHiddenKey`,
    firebaseMessagingToken: `${SETTINGS_PREFIX}firebaseMessagingToken`,
    activeChildId: `${SETTINGS_PREFIX}activeChildId`,
    darkTheme: `${SETTINGS_PREFIX}darkTheme`,
    beforeSchedule: `${SETTINGS_PREFIX}beforeSchedule`,
    afterSchedule: `${SETTINGS_PREFIX}afterSchedule`,
    lastMarksPeriod: `${SETTINGS_PREFIX}lastMarksPeriod`,
    showNullSubjectMarks: `${SETTINGS_PREFIX}showNullSubjectMarks`,
    studyLessonMenu: `${SETTINGS_PREFIX}studyLessonMenu`,
    studyMarkRating: `${SETTINGS_PREFIX}studyMarkRating`,
    studySubjectRating: `${SETTINGS_PREFIX}studySubjectRating`,
    lastStudy: `${SETTINGS_PREFIX}lastStudy`,
} as const;

export type SettingsKey = keyof typeof settingsKeys;
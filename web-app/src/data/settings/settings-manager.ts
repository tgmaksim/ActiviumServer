import { settingsKeys } from "./settings-keys";
import { getDefaultLastStudy, settingsDefaults } from "./settings-defaults";

type SettingValue = string | number | boolean | null;

function readValue<T extends SettingValue>(
    key: string,
    defaultValue: T,
): T {
    const value = localStorage.getItem(key);

    if (value === null) {
        return defaultValue;
    }

    try {
        return JSON.parse(value) as T;
    } catch {
        return defaultValue;
    }
}

function writeValue(key: string, value: SettingValue): void {
    if (value === null) {
        localStorage.removeItem(key);
    } else {
        localStorage.setItem(key, JSON.stringify(value));
    }
}

export const SettingsManager = {
    getInstallPromptHiddenKey(): boolean {
        return readValue(
            settingsKeys.installPromptHiddenKey,
            settingsDefaults.installPromptHiddenKey,
        );
    },

    setInstallPromptHiddenKey(value: boolean): void {
        writeValue(settingsKeys.installPromptHiddenKey, value);
    },

    getFirebaseMessagingToken(): string | null {
        return readValue<string | null>(
            settingsKeys.firebaseMessagingToken,
            null,
        );
    },

    setFirebaseMessagingToken(value: string | null): void {
        writeValue(settingsKeys.firebaseMessagingToken, value);
    },

    getActiveChildId(): number {
        return readValue(
            settingsKeys.activeChildId,
            settingsDefaults.activeChildId,
        );
    },

    setActiveChildId(value: number): void {
        writeValue(settingsKeys.activeChildId, value);
    },

    getDarkTheme(): boolean {
        return readValue(
            settingsKeys.darkTheme,
            settingsDefaults.darkTheme,
        );
    },

    setDarkTheme(value: boolean): void {
        writeValue(settingsKeys.darkTheme, value);
    },

    getBeforeSchedule(): number {
        return readValue(
            settingsKeys.beforeSchedule,
            settingsDefaults.beforeSchedule,
        );
    },

    setBeforeSchedule(value: number): void {
        writeValue(settingsKeys.beforeSchedule, value);
    },

    getAfterSchedule(): number {
        return readValue(
            settingsKeys.afterSchedule,
            settingsDefaults.afterSchedule,
        );
    },

    setAfterSchedule(value: number): void {
        writeValue(settingsKeys.afterSchedule, value);
    },

    getLastMarksPeriod(): number {
        return readValue(
            settingsKeys.lastMarksPeriod,
            settingsDefaults.lastMarksPeriod,
        );
    },

    setLastMarksPeriod(value: number): void {
        writeValue(settingsKeys.lastMarksPeriod, value);
    },

    getShowNullSubjectMarks(): boolean {
        return readValue(
            settingsKeys.showNullSubjectMarks,
            settingsDefaults.showNullSubjectMarks,
        );
    },

    setShowNullSubjectMarks(value: boolean): void {
        writeValue(settingsKeys.showNullSubjectMarks, value);
    },

    getStudyLessonMenu(): boolean {
        return readValue(
            settingsKeys.studyLessonMenu,
            settingsDefaults.studyLessonMenu,
        );
    },

    setStudyLessonMenu(value: boolean): void {
        writeValue(settingsKeys.studyLessonMenu, value);
    },

    getStudyMarkRating(): boolean {
        return readValue(
            settingsKeys.studyMarkRating,
            settingsDefaults.studyMarkRating,
        );
    },

    setStudyMarkRating(value: boolean): void {
        writeValue(settingsKeys.studyMarkRating, value);
    },

    getStudySubjectRating(): boolean {
        return readValue(
            settingsKeys.studySubjectRating,
            settingsDefaults.studySubjectRating,
        );
    },

    setStudySubjectRating(value: boolean): void {
        writeValue(settingsKeys.studySubjectRating, value);
    },

    getLastStudy(): string {
        return readValue(
            settingsKeys.lastStudy,
            getDefaultLastStudy(),
        );
    },

    setLastStudy(value: string): void {
        writeValue(settingsKeys.lastStudy, value);
    },

    clearAll(): void {
        for (const key of Object.values(settingsKeys)) {
            localStorage.removeItem(key);
        }
    },
};
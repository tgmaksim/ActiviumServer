import { onScopeDispose, ref, watch } from "vue";
import { defineStore } from "pinia";

import { SettingsManager } from "@/data/settings/settings-manager";
import { settingsDefaults, getDefaultLastStudy } from "@/data/settings/settings-defaults";
import { settingsKeys } from "@/data/settings/settings-keys";

export const useSettingsStore = defineStore("settings", () => {
    const installPromptHiddenKey = ref(SettingsManager.getInstallPromptHiddenKey());
    const firebaseMessagingToken = ref(SettingsManager.getFirebaseMessagingToken());
    const activeChildId = ref(SettingsManager.getActiveChildId());
    const darkTheme = ref(SettingsManager.getDarkTheme());
    const beforeSchedule = ref(SettingsManager.getBeforeSchedule());
    const afterSchedule = ref(SettingsManager.getAfterSchedule());
    const lastMarksPeriod = ref(SettingsManager.getLastMarksPeriod());
    const showNullSubjectMarks = ref(SettingsManager.getShowNullSubjectMarks());
    const studyLessonMenu = ref(SettingsManager.getStudyLessonMenu());
    const studyMarkRating = ref(SettingsManager.getStudyMarkRating());
    const studySubjectRating = ref(SettingsManager.getStudySubjectRating());
    const lastStudy = ref(SettingsManager.getLastStudy());

    let syncingFromStorage = false;

    watch(installPromptHiddenKey, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setInstallPromptHiddenKey(value);
        }
    }, { flush: "sync" });

    watch(firebaseMessagingToken, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setFirebaseMessagingToken(value);
        }
    }, { flush: "sync" });

    watch(activeChildId, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setActiveChildId(value);
        }
    }, { flush: "sync" });

    watch(darkTheme, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setDarkTheme(value);
        }
    }, { flush: "sync" });

    watch(beforeSchedule, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setBeforeSchedule(value);
        }
    }, { flush: "sync" });

    watch(afterSchedule, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setAfterSchedule(value);
        }
    }, { flush: "sync" });

    watch(lastMarksPeriod, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setLastMarksPeriod(value);
        }
    }, { flush: "sync" });

    watch(showNullSubjectMarks, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setShowNullSubjectMarks(value);
        }
    }, { flush: "sync" });

    watch(studyLessonMenu, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setStudyLessonMenu(value);
        }
    }, { flush: "sync" });

    watch(studyMarkRating, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setStudyMarkRating(value);
        }
    }, { flush: "sync" });

    watch(studySubjectRating, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setStudySubjectRating(value);
        }
    }, { flush: "sync" });

    watch(lastStudy, (value) => {
        if (!syncingFromStorage) {
            SettingsManager.setLastStudy(value);
        }
    }, { flush: "sync" });

    function loadAllFromStorage(): void {
        installPromptHiddenKey.value = SettingsManager.getInstallPromptHiddenKey();
        firebaseMessagingToken.value = SettingsManager.getFirebaseMessagingToken();
        activeChildId.value = SettingsManager.getActiveChildId();
        darkTheme.value = SettingsManager.getDarkTheme();
        beforeSchedule.value = SettingsManager.getBeforeSchedule();
        afterSchedule.value = SettingsManager.getAfterSchedule();
        lastMarksPeriod.value = SettingsManager.getLastMarksPeriod();
        showNullSubjectMarks.value = SettingsManager.getShowNullSubjectMarks();
        studyLessonMenu.value = SettingsManager.getStudyLessonMenu();
        studyMarkRating.value = SettingsManager.getStudyMarkRating();
        studySubjectRating.value = SettingsManager.getStudySubjectRating();
        lastStudy.value = SettingsManager.getLastStudy();
    }

    function syncFromStorage(key: string | null): void {
        syncingFromStorage = true;

        try {
            if (key === null) {
                loadAllFromStorage();
                return;
            }

            switch (key) {
                case settingsKeys.installPromptHiddenKey:
                    installPromptHiddenKey.value = SettingsManager.getInstallPromptHiddenKey();
                    break;
                case settingsKeys.firebaseMessagingToken:
                    firebaseMessagingToken.value = SettingsManager.getFirebaseMessagingToken();
                    break;
                case settingsKeys.activeChildId:
                    activeChildId.value = SettingsManager.getActiveChildId();
                    break;
                case settingsKeys.darkTheme:
                    darkTheme.value = SettingsManager.getDarkTheme();
                    break;
                case settingsKeys.beforeSchedule:
                    beforeSchedule.value = SettingsManager.getBeforeSchedule();
                    break;
                case settingsKeys.afterSchedule:
                    afterSchedule.value = SettingsManager.getAfterSchedule();
                    break;
                case settingsKeys.lastMarksPeriod:
                    lastMarksPeriod.value = SettingsManager.getLastMarksPeriod();
                    break;
                case settingsKeys.showNullSubjectMarks:
                    showNullSubjectMarks.value = SettingsManager.getShowNullSubjectMarks();
                    break;
                case settingsKeys.studyLessonMenu:
                    studyLessonMenu.value = SettingsManager.getStudyLessonMenu();
                    break;
                case settingsKeys.studyMarkRating:
                    studyMarkRating.value = SettingsManager.getStudyMarkRating();
                    break;
                case settingsKeys.studySubjectRating:
                    studySubjectRating.value = SettingsManager.getStudySubjectRating();
                    break;
                case settingsKeys.lastStudy:
                    lastStudy.value = SettingsManager.getLastStudy();
                    break;
            }
        } finally {
            syncingFromStorage = false;
        }
    }

    function handleStorage(event: StorageEvent): void {
        if (event.storageArea !== localStorage) {
            return;
        }

        if (event.key === null || Object.values(settingsKeys).includes(
            event.key as typeof settingsKeys[keyof typeof settingsKeys],
        )) {
            syncFromStorage(event.key);
        }
    }

    if (typeof window !== "undefined") {
        window.addEventListener("storage", handleStorage);

        onScopeDispose(() => {
            window.removeEventListener("storage", handleStorage);
        });
    }

    function reset(): void {
        syncingFromStorage = true;

        try {
            SettingsManager.clearAll();

            installPromptHiddenKey.value = settingsDefaults.installPromptHiddenKey;
            firebaseMessagingToken.value = null;
            activeChildId.value = settingsDefaults.activeChildId;
            darkTheme.value = settingsDefaults.darkTheme;
            beforeSchedule.value = settingsDefaults.beforeSchedule;
            afterSchedule.value = settingsDefaults.afterSchedule;
            lastMarksPeriod.value = settingsDefaults.lastMarksPeriod;
            showNullSubjectMarks.value = settingsDefaults.showNullSubjectMarks;
            studyLessonMenu.value = settingsDefaults.studyLessonMenu;
            studyMarkRating.value = settingsDefaults.studyMarkRating;
            studySubjectRating.value = settingsDefaults.studySubjectRating;
            lastStudy.value = getDefaultLastStudy();
        } finally {
            syncingFromStorage = false;
        }
    }

    return {
        installPromptHiddenKey,
        firebaseMessagingToken,
        activeChildId,
        darkTheme,
        beforeSchedule,
        afterSchedule,
        lastMarksPeriod,
        showNullSubjectMarks,
        studyLessonMenu,
        studyMarkRating,
        studySubjectRating,
        lastStudy,
        reset,
    };
});
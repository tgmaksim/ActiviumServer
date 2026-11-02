<template>
    <div class="schedule-page">
        <span
            v-if="isRefreshing"
            class="schedule-refresh-loader"
            aria-label="Загрузка расписания"
        ></span>

        <div class="schedule-calendar-container">
            <CalendarSkeleton
                v-if="isLoading"
                :count="10"
            />

            <CalendarStrip
                v-else
                :dates="dates"
                :selected-date="selectedDate"
                @select="onCalendarDateSelect"
            />
        </div>

        <DayPager
            :days="scheduleDays"
            :selected-date="selectedDate"
            :loading="isLoading"
            @change="onPagerDateChange"
            @praise="openPraiseDialog"
            @rating="openRating"
            @menu="openLessonMenu"
        />

        <PraiseDialog
            :visible="showPraiseDialog"
            @close="showPraiseDialog = false"
            @submit="submitPraise"
        />

        <RatingSheet
            v-if="selectedRatingLesson"
            v-model="showRatingSheet"
            :lesson="selectedRatingLesson"
            @praise="openPraiseDialog"
        />

        <LessonMenu
            v-if="selectedMenuLesson"
            v-model="showLessonMenu"
            :lesson="selectedMenuLesson"
            @note="openNoteEditor"
            @delete-note="openDeleteNoteDialog"
            @praise="openMenuPraise"
            @rating="openMenuRating"
            @dnevnik="openLessonDnevnik"
        />

        <NoteEditorDialog
            :visible="showNoteEditor"
            :note="selectedMenuLesson?.note ?? null"
            :timezone="scheduleData?.timezone ?? timezoneOffsetSeconds"
            @close="closeNoteEditor"
            @submit="submitLessonNote"
        />

        <AppDialog
            :visible="showDeleteNoteDialog"
            :title="strings.titleDialogDeleteNote"
            :message="strings.messageDialogDeleteNote"
            :action-text="strings.buttonDialogDeleteNote"
            :cancel-text="strings.cancel"
            @action="confirmDeleteNote"
            @cancel="cancelDeleteNote"
        />
    </div>
</template>

<script setup lang="ts">
import {
    computed,
    ref,
    watch,
} from "vue";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";
import { useSettingsStore } from "@/stores/settings";
import { setShownError } from "@/ui-core/state-utils";
import { LoadState } from "@/ui-core/load-state";

import CalendarStrip from "./components/CalendarStrip.vue";
import DayPager from "./components/DayPager.vue";
import CalendarSkeleton from "./skeleton/CalendarSkeleton.vue";
import PraiseDialog from "@/components/PraiseDialog.vue";
import RatingSheet from "./rating/RatingSheet.vue";
import AppDialog from "@/components/AppDialog.vue";
import LessonMenu from "./components/LessonMenu.vue";
import NoteEditorDialog from "./components/NoteEditorDialog.vue";

import { ScheduleViewModel } from "./schedule-view-model";

import {
    addDays,
    buildDateRange,
    getCurrentDateInTimezone,
    getCurrentHourInTimezone,
    getDefaultScheduleDate,
} from "./date-utils";

import type {
    ScheduleDate,
    SchedulePagerDay,
    UiScheduleDay,
    UiScheduleLesson,
} from "./types";

import {
    useConfetti,
} from "@/composables/useConfetti";
import type { ConfettiOptions } from "@/utils/confetti/confetti-engine";

const {
    startConfettiAnimation,
} = useConfetti();

const settings = useSettingsStore();
const scheduleViewModel = new ScheduleViewModel();

const scheduleData = computed(
    () => scheduleViewModel.scheduleData.value,
);

const scheduleState = computed(
    () => scheduleViewModel.scheduleState.value,
);

/**
 * Пока кэш не прочитан, данные отсутствуют
 * и продолжают отображаться skeleton-компоненты.
 */
const isLoading = computed(
    () => scheduleData.value === null,
);

/**
 * Обновление с сервера не скрывает уже загруженное расписание.
 */
const isRefreshing = computed(
    () => scheduleState.value.type === "cloudLoading",
);

/**
 * Ошибка уже показана пользователю.
 * Повторный запрос запускается нажатием на крест.
 */
const isScheduleError = computed(
    () => scheduleState.value.type === "shownError",
);

/**
 * Часовой пояс браузера используется до получения
 * часового пояса из кэша или ответа сервера.
 */
const timezoneOffsetSeconds = ref(
    -new Date().getTimezoneOffset() * 60,
);

const today = computed(() =>
    getCurrentDateInTimezone(timezoneOffsetSeconds.value),
);

const dates = computed(() =>
    buildDateRange(
        today.value,
        settings.beforeSchedule,
        settings.afterSchedule,
    ),
);

const defaultDate = computed(() =>
    getDefaultScheduleDate(
        today.value,
        getCurrentHourInTimezone(timezoneOffsetSeconds.value),
    ),
);

/**
 * Единственный источник выбранной даты.
 */
const selectedDate = ref<ScheduleDate>(
    defaultDate.value,
);

/**
 * Сопоставляем нормализованные дни ViewModel
 * с датами календаря.
 *
 * Обёртка сохраняет дату даже тогда, когда данных
 * для неё пока нет (null). Это необходимо для свайпов.
 */
const scheduleDays = computed<SchedulePagerDay[]>(() => {
    const praiseStates = scheduleViewModel.praiseStates.value;
    const byDate = new Map<ScheduleDate, UiScheduleDay>();

    for (const day of scheduleData.value?.schedule ?? []) {
        if (day) {
            byDate.set(day.date, day);
        }
    }

    return dates.value.map((date) => {
        const day = byDate.get(date);

        if (!day) {
            return {
                date,
                data: null,
            };
        }

        return {
            date,
            data: {
                ...day,
                lessons: day.lessons.map((lesson) => {
                    if (!lesson.lessonKey) {
                        return lesson;
                    }

                    const praiseState = praiseStates.get(lesson.lessonKey);
                    const noteState = scheduleViewModel.noteStates.value.get(
                        lesson.lessonKey,
                    );

                    if (!praiseState && !noteState) {
                        return lesson;
                    }

                    return {
                        ...lesson,
                        praiseState: praiseState
                            ? praiseState as UiScheduleLesson["praiseState"]
                            : lesson.praiseState,
                        noteState: noteState ?? lesson.noteState,
                    };
                }),
            },
        };
    });
});

const showPraiseDialog = ref(false);
const selectedPraiseLessonKey = ref<string | null>(null);
const activeConfettiOptions = ref<ConfettiOptions | null>(null);

const showRatingSheet = ref(false);
const selectedRatingLessonKey = ref<string | null>(null);

const showLessonMenu = ref(false);
const showNoteEditor = ref(false);
const showDeleteNoteDialog = ref(false);

const selectedLessonKey = ref<string | null>(null);

const selectedMenuLesson = computed<UiScheduleLesson | null>(() => {
    const lessonKey = selectedLessonKey.value;

    if (!lessonKey) {
        return null;
    }

    const lesson = scheduleData.value?.schedule
        .flatMap(day => day?.lessons ?? [])
        .find(item => item.lessonKey === lessonKey);

    if (!lesson) {
        return null;
    }

    const praiseState = scheduleViewModel.praiseStates.value.get(
        lessonKey,
    );

    const noteState = scheduleViewModel.noteStates.value.get(
        lessonKey,
    );

    return {
        ...lesson,
        praiseState: praiseState
            ? praiseState as UiScheduleLesson["praiseState"]
            : lesson.praiseState,
        noteState: noteState ?? lesson.noteState,
    };
});

function openLessonMenu(lessonKey: string): void {
    const lesson = scheduleData.value?.schedule
        .flatMap(day => day?.lessons ?? [])
        .find(item => item.lessonKey === lessonKey);

    if (!lesson || lesson.isExtra || !lesson.lessonKey) {
        return;
    }

    selectedLessonKey.value = lessonKey;
    showLessonMenu.value = true;
}

function openNoteEditor(): void {
    if (!selectedMenuLesson.value) {
        return;
    }

    showNoteEditor.value = true;
}

function closeNoteEditor(): void {
    showNoteEditor.value = false;
    selectedLessonKey.value = null;
}

function submitLessonNote(data: {
    text: string;
    public: boolean;
    remindTime: string | null;
}): void {
    const lessonKey = selectedLessonKey.value;

    if (!lessonKey) {
        return;
    }

    showNoteEditor.value = false;

    scheduleViewModel.createLessonNote(
        lessonKey,
        data.text,
        data.public,
        data.remindTime,
    );

    selectedLessonKey.value = null;
}

function openDeleteNoteDialog(): void {
    if (!selectedMenuLesson.value?.note?.text.trim()) {
        return;
    }

    showDeleteNoteDialog.value = true;
}

function cancelDeleteNote(): void {
    showDeleteNoteDialog.value = false;
    selectedLessonKey.value = null;
}

function confirmDeleteNote(): void {
    const lessonKey = selectedLessonKey.value;

    showDeleteNoteDialog.value = false;

    if (!lessonKey) {
        return;
    }

    scheduleViewModel.deleteLessonNote(lessonKey);
    selectedLessonKey.value = null;
}

function openMenuPraise(): void {
    const lessonKey = selectedLessonKey.value;

    if (!lessonKey) {
        return;
    }

    openPraiseDialog(lessonKey, {});
    selectedLessonKey.value = null;
}

function openMenuRating(): void {
    const lessonKey = selectedLessonKey.value;

    if (!lessonKey) {
        return;
    }

    openRating(lessonKey);
    selectedLessonKey.value = null;
}

function openLessonDnevnik(): void {
    const url = selectedMenuLesson.value?.dnevnikruUrl;

    if (url) {
        window.open(url, "_blank", "noopener,noreferrer");
    }

    selectedLessonKey.value = null;
}

const selectedRatingLesson = computed<UiScheduleLesson | null>(() => {
    const lessonKey = selectedRatingLessonKey.value;

    if (!lessonKey) {
        return null;
    }

    for (const day of scheduleData.value?.schedule ?? []) {
        const lesson = day?.lessons.find(
            item => item.lessonKey === lessonKey,
        );

        if (!lesson) {
            continue;
        }

        const praiseState = scheduleViewModel.praiseStates.value.get(
            lessonKey,
        );

        if (!praiseState) {
            return lesson;
        }

        return {
            ...lesson,
            praiseState: praiseState as UiScheduleLesson["praiseState"],
        };
    }

    return null;
});

function openRating(lessonKey: string): void {
    const lesson = scheduleData.value?.schedule
        .flatMap(day => day?.lessons ?? [])
        .find(item => item.lessonKey === lessonKey);

    if (!lesson?.ratingKey) {
        return;
    }

    selectedRatingLessonKey.value = lessonKey;
    showRatingSheet.value = true;
}

/**
 * Получение часового пояса из ViewModel.
 */
watch(
    () => scheduleData.value?.timezone,
    (timezone) => {
        if (typeof timezone !== "number") {
            return;
        }

        timezoneOffsetSeconds.value = timezone;
    },
);

/**
 * Сохраняем выбранную дату, если она остаётся доступной.
 * Иначе открываем дату по правилам Android.
 */
watch(
    dates,
    (newDates) => {
        if (newDates.includes(selectedDate.value)) {
            return;
        }

        selectedDate.value =
            newDates.find(date => date === defaultDate.value) ??
            newDates.find(date => date === today.value) ??
            newDates[0];
    },
);

/**
 * Реакция на изменение активного ребёнка
 * и диапазона расписания.
 *
 * Поведение повторяет Android:
 * - смена ребёнка начинает загрузку с нуля;
 * - изменение диапазона сохраняет уже имеющиеся дни;
 * - при появлении пропусков перечитывается кэш,
 *   после чего ViewModel обновляет расписание с сервера.
 */
watch(
    () => [
        settings.activeChildId,
        settings.beforeSchedule,
        settings.afterSchedule,
    ] as const,
    (
        [childId, before, after],
        [previousChildId, previousBefore, previousAfter],
    ) => {
        if (childId !== previousChildId) {
            showRatingSheet.value = false;
            selectedRatingLessonKey.value = null;

            selectedDate.value = defaultDate.value;
            scheduleViewModel.resetSchedule();

            showLessonMenu.value = false;
            showNoteEditor.value = false;
            showDeleteNoteDialog.value = false;
            selectedLessonKey.value = null;

            return;
        }

        if (
            before === previousBefore &&
            after === previousAfter
        ) {
            return;
        }

        const currentData = scheduleData.value;

        if (!currentData) {
            scheduleViewModel.resetSchedule();
            return;
        }

        const newDates = buildDateRange(
            getCurrentDateInTimezone(currentData.timezone),
            before,
            after,
        );

        const byDate = new Map(
            currentData.schedule
                .filter((day): day is UiScheduleDay => day !== null)
                .map(day => [day.date, day]),
        );

        const newSchedule = newDates.map(
            date => byDate.get(date) ?? null,
        );

        scheduleViewModel.scheduleData.value = {
            ...currentData,
            schedule: newSchedule,
        };

        if (newSchedule.some(day => day === null)) {
            scheduleViewModel.loadCacheSchedule();
        }
    },
);

/**
 * Обработка состояний загрузки.
 *
 * Последовательность:
 * Empty → CacheLoading → CacheSuccess → CloudLoading → CloudSuccess.
 */
watch(
    scheduleState,
    (state) => {
        switch (state.type) {
            case "empty":
                scheduleViewModel.loadCacheSchedule();
                break;

            case "cacheLoading":
                break;

            case "cacheSuccess":
                scheduleViewModel.loadCloudSchedule();
                break;

            case "cloudLoading":
                scheduleViewModel.emptyStates();
                break;

            case "cloudSuccess":
                break;

            case "cloudError":
                Utilities.showUiMessage(state.message);

                setShownError(scheduleViewModel.scheduleState);

                break;

            case "shownError":
                break;
        }
    },
    {
        immediate: true,
    },
);

watch(
    () => scheduleViewModel.praiseStates.value,
    (states) => {
        for (const [lessonKey, state] of states) {
            if (state.type === "success") {
                const confettiOptions = activeConfettiOptions.value ?? {};
                activeConfettiOptions.value = null;
                startConfettiAnimation(confettiOptions);
                scheduleViewModel.praiseStates.value.delete(lessonKey);
            }

            if (state.type !== "error") {
                continue;
            }

            Utilities.showUiMessage(state.message);

            const updatedStates = new Map(
                scheduleViewModel.praiseStates.value,
            );

            updatedStates.set(
                lessonKey,
                setShownError(state),
            );

            scheduleViewModel.praiseStates.value = updatedStates;
        }
    },
);

watch(
    () => scheduleViewModel.noteStates.value,
    (states) => {
        for (const [lessonKey, state] of states) {
            if (state.type !== "error") {
                continue;
            }

            Utilities.showUiMessage(state.message);

            const updatedStates = new Map(
                scheduleViewModel.noteStates.value,
            );

            updatedStates.set(
                lessonKey,
                LoadState.shownError(),
            );

            scheduleViewModel.noteStates.value = updatedStates;
        }
    },
);

/**
 * Выбор даты через календарь.
 */
function onCalendarDateSelect(date: ScheduleDate): void {
    if (!dates.value.includes(date)) {
        return;
    }

    selectedDate.value = date;
}

/**
 * Смена даты через горизонтальный свайп.
 */
function onPagerDateChange(date: ScheduleDate): void {
    if (!dates.value.includes(date)) {
        return;
    }

    selectedDate.value = date;
}

function openPraiseDialog(lessonKey: string, konfettiOptions: ConfettiOptions): void {
    if (
        scheduleViewModel.praiseStates.value.get(lessonKey)?.type === "loading"
    ) {
        return;
    }

    selectedPraiseLessonKey.value = lessonKey;
    activeConfettiOptions.value = konfettiOptions;
    showPraiseDialog.value = true;
}

function submitPraise(text: string | null): void {
    const lessonKey = selectedPraiseLessonKey.value;
    const confettiOptions = activeConfettiOptions.value ?? {};

    if (!lessonKey) {
        return;
    }

    if (
        scheduleViewModel.praiseStates.value.get(lessonKey)?.type === "loading"
    ) {
        return;
    }

    showPraiseDialog.value = false;
    scheduleViewModel.sendPraise(lessonKey, text);
}
</script>

<style scoped>
.schedule-page {
    display: flex;
    flex-direction: column;

    width: 100%;
    height: 100%;

    max-width: 720px;
    margin-inline: auto;

    min-width: 0;
    min-height: 0;

    padding-top: 5px;

    overflow: hidden;
}

.schedule-calendar-container {
    position: relative;
    flex: 0 0 auto;

    width: 100%;

    margin-bottom: 10px;
}

.schedule-page > :deep(.schedule-day-pager) {
    flex: 1 1 0;

    min-width: 0;
    min-height: 0;
}

.schedule-refresh-loader {
    position: absolute;
    top: 100px;
    right: 50%;

    display: inline-block;

    width: 30px;
    height: 30px;

    border: 5px solid var(--stroke-bg);
    border-top-color: var(--slider-accent);
    border-radius: 50%;

    animation: schedule-loader 0.7s linear infinite;

    transform: translateY(-50%);

    z-index: 1000;
}

@keyframes schedule-loader {
    to {
        transform: translateY(-50%) rotate(360deg);
    }
}
</style>
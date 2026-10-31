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

import CalendarStrip from "./components/CalendarStrip.vue";
import DayPager from "./components/DayPager.vue";
import CalendarSkeleton from "./skeleton/CalendarSkeleton.vue";

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
} from "./types";

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
    const byDate = new Map<ScheduleDate, UiScheduleDay>();

    for (const day of scheduleData.value?.schedule ?? []) {
        if (day) {
            byDate.set(day.date, day);
        }
    }

    return dates.value.map(date => ({
        date,
        data: byDate.get(date) ?? null,
    }));
});

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
            selectedDate.value = defaultDate.value;
            scheduleViewModel.resetSchedule();
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

                scheduleViewModel.scheduleState.value =
                    setShownError(state);

                break;

            case "shownError":
                break;
        }
    },
    {
        immediate: true,
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
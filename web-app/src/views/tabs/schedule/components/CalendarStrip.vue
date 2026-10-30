<template>
    <div
        ref="calendar"
        class="schedule-calendar"
        role="group"
        aria-label="Календарь расписания"
    >
        <button
            v-for="date in dates"
            :key="date"
            :ref="element => setDateElement(date, element)"
            class="calendar-day"
            :class="{
                'calendar-day-selected': date === selectedDate,
            }"
            type="button"
            :aria-pressed="date === selectedDate"
            @click="selectDate(date)"
        >
            <span class="calendar-weekday">
                {{ getWeekday(date) }}
            </span>

            <span class="calendar-day-number">
                {{ getDayNumber(date) }}
            </span>
        </button>
    </div>
</template>

<script setup lang="ts">
import {
    nextTick,
    onMounted,
    ref,
    watch,
} from "vue";

import type { ScheduleDate } from "../types";

const props = defineProps<{
    dates: readonly ScheduleDate[];
    selectedDate: ScheduleDate;
}>();

const emit = defineEmits<{
    select: [date: ScheduleDate];
}>();

const calendar = ref<HTMLElement | null>(null);

const dateElements = new Map<ScheduleDate, HTMLElement>();

const weekdayFormatter = new Intl.DateTimeFormat(
    "ru-RU",
    {
        weekday: "short",
        timeZone: "UTC",
    },
);

function getDateObject(date: ScheduleDate): Date {
    return new Date(`${date}T12:00:00Z`);
}

function getWeekday(date: ScheduleDate): string {
    return weekdayFormatter
        .format(getDateObject(date))
        .replace(/\.$/, "")
        .toUpperCase();
}

function getDayNumber(date: ScheduleDate): number {
    return Number(date.slice(8, 10));
}

function setDateElement(
    date: ScheduleDate,
    element: Element | null,
): void {
    if (element instanceof HTMLElement) {
        dateElements.set(date, element);
    } else {
        dateElements.delete(date);
    }
}

function centerSelectedDate(): void {
    const container = calendar.value;
    const element = dateElements.get(props.selectedDate);

    if (!container || !element) {
        return;
    }

    const left =
        element.offsetLeft -
        (container.clientWidth - element.offsetWidth) / 2;

    container.scrollTo({
        left,
        behavior: "smooth",
    });
}

function selectDate(date: ScheduleDate): void {
    if (date === props.selectedDate) {
        return;
    }

    emit("select", date);
}

watch(
    () => [props.selectedDate, props.dates] as const,
    async () => {
        await nextTick();
        centerSelectedDate();
    },
    { flush: "post" },
);

onMounted(() => {
    centerSelectedDate();
});
</script>

<style scoped>
.schedule-calendar {
    display: flex;
    align-items: center;

    gap: 14px;

    width: 100%;
    min-width: 0;

    padding: 0 5px;

    overflow-x: auto;
    overflow-y: hidden;

    scrollbar-width: none;
    overscroll-behavior-x: contain;
}

.schedule-calendar::-webkit-scrollbar {
    display: none;
}

.calendar-day {
    display: flex;
    flex: 0 0 45px;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;

    width: 45px;
    height: 45px;

    padding: 3px 0;

    border: 1px solid var(--calendar-day-stroke);
    border-radius: 12px;

    background: var(--calendar-day-fill);
    color: var(--text-primary);

    cursor: pointer;
    -webkit-tap-highlight-color: transparent;

    transition:
        background-color 180ms ease,
        border-color 180ms ease,
        transform 120ms ease;
}

.calendar-day:active {
    transform: scale(0.95);
}

.calendar-day-selected {
    background: var(--calendar-day-selected-fill);
    border-color: var(--calendar-day-selected-stroke);
}

.calendar-weekday {
    font-family: sans-serif;
    font-size: 11px;
    font-weight: 500;
    line-height: 14px;
    opacity: 0.7;
}

.calendar-day-number {
    font-family: sans-serif;
    font-size: 24px;
    font-weight: 500;
    line-height: 25px;
}
</style>
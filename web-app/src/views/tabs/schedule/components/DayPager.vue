<template>
    <div class="schedule-day-pager">
        <DaySkeleton v-if="loading" />

        <Swiper
            v-else
            :initial-slide="selectedIndex"
            :slides-per-view="1"
            :space-between="0"
            :speed="260"
            :threshold="8"
            :resistance="true"
            :resistance-ratio="0.85"
            :touch-angle="35"
            :nested="true"
            :allow-touch-move="true"
            class="schedule-swiper"
            no-swiping-class="swiper-no-swiping"
            @swiper="onSwiper"
            @slideChange="onSlideChange"
        >
            <SwiperSlide
                v-for="(day, dayIndex) in days"
                :key="day.date"
                class="schedule-swiper-slide"
            >
                <div class="schedule-day-scroll">
                    <DaySkeleton
                        v-if="day.data === null"
                    />

                    <img
                        v-else-if="isWeekend(day.data)"
                        :src="weekendImage"
                        class="schedule-weekend"
                        alt=""
                    />

                    <div
                        v-else
                        class="schedule-day-content"
                    >
                        <LessonCard
                            v-for="item in getDisplayLessons(day.data)"
                            :key="item.key"
                            :lesson="item.lesson"
                            :number="item.number"
                        />
                    </div>
                </div>
            </SwiperSlide>
        </Swiper>
    </div>
</template>

<script setup lang="ts">
import {
    computed,
    nextTick,
    shallowRef,
    watch,
} from "vue";

import { Swiper, SwiperSlide } from "swiper/vue";
import type { Swiper as SwiperInstance } from "swiper";

import "swiper/css";

import weekendImage from "@/assets/weekend.png";

import DaySkeleton from "../skeleton/DaySkeleton.vue";
import LessonCard from "./LessonCard.vue";

import type {
    SchedulePagerDay,
    ScheduleDate,
    UiScheduleDay,
    UiScheduleLesson,
} from "../types";

const props = defineProps<{
    days: readonly SchedulePagerDay[];
    selectedDate: ScheduleDate;
    loading: boolean;
}>();

const emit = defineEmits<{
    change: [date: ScheduleDate];
}>();

const swiperInstance = shallowRef<SwiperInstance | null>(null);

const selectedIndex = computed(() => {
    const index = props.days.findIndex(
        day => day.date === props.selectedDate,
    );

    return Math.max(0, index);
});

/**
 * Сохраняем экземпляр Swiper.
 */
function onSwiper(swiper: SwiperInstance): void {
    swiperInstance.value = swiper;
}

/**
 * Проверяем, является ли день выходным.
 *
 * Школьные посты здесь намеренно не учитываются:
 * их отображение пока не входит в текущую задачу.
 */
function isWeekend(day: UiScheduleDay): boolean {
    return (
        day.lessons.length === 0 &&
        day.ea.length === 0
    );
}

/**
 * Преобразуем внеурочное занятие в обычную модель карточки.
 *
 * Поведение повторяет ScheduleExtracurricularActivity.toUiScheduleLesson()
 * из Android.
 */
function toExtraLesson(
    activity: UiScheduleDay["ea"][number],
): UiScheduleLesson {
    return {
        lessonKey: null,
        number: 0,

        subject: activity.subject,
        place: activity.place,
        hours: activity.hours,

        works: [],
        logs: [],
        othersMarks: [],
        avgGroupLessonMark: null,

        homework: null,
        note: null,
        files: [],

        ratingKey: null,
        dnevnikruUrl: null,

        praiseState: null,
        noteState: null,

        isExtra: true,
    };
}

interface DisplayLesson {
    key: string;
    number: number;
    lesson: UiScheduleLesson;
}

/**
 * Сначала обычные уроки в порядке номера,
 * затем внеурочные занятия.
 */
function getDisplayLessons(day: UiScheduleDay): DisplayLesson[] {
    const lessons = [...day.lessons]
        .sort((a, b) => a.number - b.number);

    return [
        ...lessons.map((lesson, index) => ({
            key: lesson.lessonKey ?? `${day.date}-lesson-${index}`,
            number: index + 1,
            lesson,
        })),

        ...day.ea.map((activity, index) => ({
            key: `${day.date}-extra-${index}`,
            number: lessons.length + index + 1,
            lesson: toExtraLesson(activity),
        })),
    ];
}

/**
 * Переключение даты через свайп.
 */
function onSlideChange(swiper: SwiperInstance): void {
    const day = props.days[swiper.activeIndex];

    if (!day || day.date === props.selectedDate) {
        return;
    }

    emit("change", day.date);
}

/**
 * Синхронизация Swiper с выбранной датой календаря.
 */
async function syncSelectedDate(): Promise<void> {
    await nextTick();

    const swiper = swiperInstance.value;

    if (!swiper || swiper.destroyed) {
        return;
    }

    swiper.update();

    const index = selectedIndex.value;

    if (swiper.activeIndex !== index) {
        swiper.slideTo(index);
    }
}

watch(
    () => [props.selectedDate, props.days] as const,
    syncSelectedDate,
);

watch(
    () => props.loading,
    async (loading) => {
        if (!loading) {
            await nextTick();
            await syncSelectedDate();
        }
    },
);
</script>

<style scoped>
.schedule-day-pager {
    flex: 1 1 0;

    width: 100%;
    min-width: 0;
    min-height: 0;

    overflow: hidden;
}

.schedule-swiper {
    width: 100%;
    height: 100%;
}

.schedule-swiper-slide {
    width: 100%;
    height: 100%;

    overflow: hidden;
}

.schedule-day-scroll {
    width: 100%;
    height: 100%;

    overflow-x: hidden;
    overflow-y: auto;

    overscroll-behavior-y: contain;
    touch-action: pan-y;

    scrollbar-width: none;

    -webkit-user-select: text;
    user-select: text;
}

.schedule-day-scroll::-webkit-scrollbar {
    display: none;
}

.schedule-day-content {
    display: flex;
    flex-direction: column;

    width: 100%;
    min-height: 100%;

    padding: 6px 5px 110px;
}

.schedule-weekend {
    display: block;

    width: 100%;
    height: 100%;

    object-fit: cover;
}
</style>
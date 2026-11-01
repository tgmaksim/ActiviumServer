<template>
    <BottomSheet
        v-model="isOpen"
        :aria-label="strings.openRating"
    >
        <div class="rating-sheet">
            <div
                v-if="showMainLoader"
                class="rating-loader-container"
            >
                <span class="rating-loader"></span>
            </div>

            <div
                v-if="showStats"
                class="rating-stats"
            >
                <div
                    v-if="ratingData?.oldAvgMark"
                    class="rating-mark"
                    :class="getMarkMoodClass(ratingData.oldAvgMark.mood)"
                >
                    {{ ratingData.oldAvgMark.value }}
                </div>

                <span
                    v-else-if="showAverageLoaders"
                    class="rating-loader"
                ></span>

                <span
                    class="rating-arrow"
                    v-html="arrowRight"
                />

                <div
                    v-if="ratingData?.newAvgMark"
                    class="rating-mark"
                    :class="getMarkMoodClass(ratingData.newAvgMark.mood)"
                >
                    {{ ratingData.newAvgMark.value }}
                </div>

                <span
                    v-else-if="showAverageLoaders"
                    class="rating-loader"
                ></span>
            </div>

            <div class="rating-my-mark-row">
                <div
                    v-if="lesson.logs.length"
                    class="rating-group"
                >
                    <span class="rating-group-title">
                        {{ lesson.logs.length === 1 ? strings.myMark : strings.myMarks }}
                    </span>

                    <div class="rating-marks">
                        <span
                            v-for="(mark, index) in lesson.logs"
                            :key="index"
                            class="rating-mark"
                            :class="getMarkMoodClass(mark.mood)"
                        >
                            {{ mark.value }}
                        </span>
                    </div>
                </div>

                <button
                    v-if="showPraise"
                    class="rating-praise"
                    type="button"
                    :disabled="praiseLoading"
                    aria-label="Похвалить ребенка"
                    @click="onPraiseClick"
                >
                    <span
                        v-if="praiseLoading"
                        class="rating-loader"
                    ></span>

                    <span
                        v-else-if="praiseError"
                        class="rating-praise-error"
                    >
                        ×
                    </span>

                    <span v-else>👍</span>
                </button>
            </div>

            <div
                v-if="lesson.othersMarks.length && lesson.avgGroupLessonMark"
                class="rating-group"
            >
                <span class="rating-group-title">
                    {{ strings.avgGroupLessonMark }}
                </span>

                <div class="rating-marks">
                    <span
                        class="rating-mark"
                        :class="getMarkMoodClass(lesson.avgGroupLessonMark.mood)"
                    >
                        {{ lesson.avgGroupLessonMark.value }}
                    </span>
                </div>
            </div>

            <p class="rating-info">
                {{ infoText }}
            </p>

            <div class="rating-list">
                <div
                    v-for="(person, index) in lesson.othersMarks"
                    :key="`${person.name}-${index}`"
                    class="rating-person"
                    :class="{
                        'rating-person-old': person.isOldMark,
                    }"
                >
                    <span
                        v-if="showNumber"
                        class="rating-person-number"
                    >
                        {{ person.number != null
                            ? strings.personNumber(person.number + 1)
                            : ""
                        }}
                    </span>

                    <span
                        v-if="person.isRatingUp === true"
                        class="rating-person-arrow"
                        v-html="arrowUp"
                    />

                    <span
                        v-else-if="person.isRatingUp === false"
                        class="rating-person-arrow"
                        v-html="arrowDown"
                    />

                    <div class="rating-person-name">
                        <span>{{ person.name }}</span>

                        <button
                            v-if="person.isOldMark"
                            class="rating-info-button"
                            type="button"
                            :aria-label="strings.oldMarkInfo"
                            @click="showOldMarkInfo"
                        >
                            <img
                                :src="infoIcon"
                                alt=""
                            />
                        </button>
                    </div>

                    <div class="rating-person-marks">
                        <span
                            v-for="(mark, markIndex) in person.marks"
                            :key="markIndex"
                            class="rating-mark"
                            :class="getMarkMoodClass(mark.mood)"
                        >
                            {{ mark.value }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </BottomSheet>
</template>

<script setup lang="ts">
import {
    computed,
    ref,
    watch,
} from "vue";

import BottomSheet from "@/components/BottomSheet.vue";

import arrowUp from "@/assets/rating/arrow_up.svg?raw";
import arrowDown from "@/assets/rating/arrow_down.svg?raw";
import arrowRight from "@/assets/rating/arrow_right.svg?raw";
import infoIcon from "@/assets/rating/info.svg";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

import { isLoadError, setShownCacheError } from "@/ui-core/state-utils";

import { RatingViewModel } from "./rating-view-model";

import type { UiScheduleLesson } from "../types";

const props = withDefaults(
    defineProps<{
        modelValue: boolean;
        lesson: UiScheduleLesson;
        showNumber?: boolean;
    }>(),
    {
        showNumber: false,
    },
);

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
    praise: [lessonKey: string];
}>();

const ratingViewModel = new RatingViewModel();

const isOpen = computed({
    get: () => props.modelValue,
    set: value => emit("update:modelValue", value),
});

const ratingState = computed(
    () => ratingViewModel.lessonRatingState.value,
);

const ratingData = computed(
    () => ratingViewModel.lessonRatingData.value,
);

const isLoading = computed(
    () =>
        ratingState.value.type === "cacheLoading" ||
        ratingState.value.type === "cloudLoading",
);

const showMainLoader = computed(
    () => isLoading.value && ratingData.value?.newAvgMark != null,
);

const showAverageLoaders = computed(
    () => isLoading.value && ratingData.value?.newAvgMark == null,
);

const showStats = computed(
    () =>
        isLoading.value ||
        ratingData.value?.oldAvgMark != null ||
        ratingData.value?.newAvgMark != null,
);

const showPraise = computed(() =>
    !props.lesson.isExtra &&
    props.lesson.lessonKey !== null &&
    props.lesson.praiseState !== null &&
    props.lesson.logs.length > 0 &&
    props.lesson.praiseState.type !== "success",
);

const praiseLoading = computed(
    () => props.lesson.praiseState?.type === "loading",
);

const praiseError = computed(
    () => isLoadError(props.lesson.praiseState),
);

/**
 * Получаем дату первой оценки.
 *
 * Поддерживаем ISO-строку, Unix timestamp
 * и объект с epochSeconds.
 */
function parseCreatedDate(value: unknown): Date | null {
    let timestamp: number;

    if (typeof value === "number") {
        timestamp = value < 1_000_000_000_000
            ? value * 1000
            : value;
    } else if (typeof value === "string") {
        timestamp = Date.parse(value);
    } else if (
        typeof value === "object" &&
        value !== null &&
        "epochSeconds" in value &&
        typeof value.epochSeconds === "number"
    ) {
        timestamp = value.epochSeconds * 1000;
    } else {
        return null;
    }

    const date = new Date(timestamp);

    return Number.isNaN(date.getTime()) ? null : date;
}

const firstMarkDate = computed(() => {
    const dates = props.lesson.logs
        .map(mark => parseCreatedDate(
            (mark as { created?: unknown }).created,
        ))
        .filter((date): date is Date => date !== null);

    dates.sort((a, b) => a.getTime() - b.getTime());

    return dates[0] ?? null;
});

function formatDateTime(date: Date): string {
    const formattedDate = new Intl.DateTimeFormat(
        "ru-RU",
        {
            day: "numeric",
            month: "long",
        },
    ).format(date);

    const formattedTime = new Intl.DateTimeFormat(
        "ru-RU",
        {
            hour: "2-digit",
            minute: "2-digit",
            hourCycle: "h23",
        },
    ).format(date);

    return `${formattedDate} в ${formattedTime}`;
}

const infoText = computed(() => {
    const period = props.lesson.works
        .map(work => work.title)
        .join(", ");

    const additional = firstMarkDate.value
        ? strings.ratingInfoTime(
            formatDateTime(firstMarkDate.value),
        )
        : "";

    return strings.ratingInfo(
        props.lesson.subject,
        period,
        additional,
    );
});

function getMarkMoodClass(mood: string): string {
    switch (mood) {
        case "good":
            return "rating-mark-good";

        case "average":
            return "rating-mark-average";

        case "bad":
            return "rating-mark-bad";

        case "more":
        default:
            return "rating-mark-more";
    }
}

function showOldMarkInfo(): void {
    Utilities.showText(strings.oldMarkInfo, true);
}

function onPraiseClick(): void {
    const lessonKey = props.lesson.lessonKey;

    if (!lessonKey || praiseLoading.value) {
        return;
    }

    emit("praise", lessonKey);
}

/**
 * При каждом открытии или смене урока
 * загружаем его статистику.
 */
watch(
    () => [props.modelValue, props.lesson.ratingKey] as const,
    ([opened, ratingKey]) => {
        if (!opened || !ratingKey) {
            return;
        }

        ratingViewModel.resetLessonRating();

        void ratingViewModel.loadCacheLessonRatingStats(ratingKey);
    },
    {
        immediate: true,
    },
);

/**
 * Последовательность загрузки:
 * Empty → CacheLoading → CacheSuccess → CloudLoading → CloudSuccess.
 */
watch(
    ratingViewModel.lessonRatingState,
    (state) => {
        switch (state.type) {
            case "cacheSuccess":
            case "cacheError":
                if (props.modelValue && props.lesson.ratingKey) {
                    ratingViewModel.loadCloudLessonRatingStats(
                        props.lesson.ratingKey,
                    );
                }

                if (state.type === "cacheError") {
                    Utilities.showUiMessage(state.message);
                }

                break;

            case "cloudError":
                Utilities.showUiMessage(state.message);

                ratingViewModel.lessonRatingState.value = setShownCacheError(
                    ratingViewModel.lessonRatingState,
                );

                break;
        }
    },
    {
        immediate: true,
    },
);
</script>

<style scoped>
.rating-sheet {
    box-sizing: border-box;
    width: 100%;
    padding: 0 10px 16px;
}

.rating-loader-container {
    display: flex;
    justify-content: center;
    padding: 10px 0;
}

.rating-loader {
    display: inline-block;
    flex: 0 0 auto;

    width: 18px;
    height: 18px;

    border: 2px solid var(--stroke-bg);
    border-top-color: var(--slider-accent);
    border-radius: 50%;

    animation: rating-loader 0.7s linear infinite;
}

.rating-stats {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    min-height: 42px;
    margin: 8px 0 12px;
}

.rating-arrow {
    width: 20px;
    height: 20px;
    object-fit: contain;
}

.rating-mark {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    box-sizing: border-box;
    min-width: 32px;
    height: 32px;
    padding: 4px;

    border-radius: 5px;

    color: #fff;
    font-family: sans-serif;
    font-size: 20px;
    font-weight: 500;
    line-height: 1;
}

.rating-mark-good {
    background: var(--mark-log-good);
}

.rating-mark-average {
    background: var(--mark-log-average);
}

.rating-mark-bad {
    background: var(--mark-log-bad);
}

.rating-mark-more {
    background: var(--mark-log-more);
}

.rating-my-mark-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.rating-group {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;

    width: 100%;
    padding: 4px 5px;
}

.rating-group-title {
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 600;
}

.rating-marks {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;
    margin-left: auto;
}

.rating-praise {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    width: 38px;
    height: 38px;
    margin-left: auto;

    border: 1px solid var(--stroke-bg);
    border-radius: 50%;

    background: var(--button-bg);
    color: var(--lesson-like-icon);

    font-size: 23px;
    line-height: 1;

    cursor: pointer;
}

.rating-praise:disabled {
    cursor: default;
}

.rating-praise-error {
    color: #e53935;
    font-size: 26px;
}

.rating-info {
    margin: 10px 5px 0;

    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.4;
}

.rating-list {
    display: flex;
    flex-direction: column;
    gap: 3px;

    margin-top: 12px;
    padding-bottom: 12px;
}

.rating-person {
    display: flex;
    align-items: center;
    gap: 5px;

    min-width: 0;
    padding: 4px 5px;
}

.rating-person-old {
    border-radius: 8px;
    background: var(--button-bg);
}

.rating-person-number {
    flex: 0 0 auto;

    color: var(--text-primary);
    font-size: 15px;
    font-weight: 700;
}

.rating-person-arrow {
    flex: 0 0 auto;

    width: 18px;
    height: 22px;

    object-fit: contain;
}

.rating-person-name {
    display: flex;
    flex: 1 1 auto;
    align-items: center;
    gap: 4px;

    min-width: 0;
    margin-left: 5px;

    color: var(--text-primary);
    font-size: 15px;
    font-weight: 700;
}

.rating-person-name > span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.rating-info-button {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    width: 22px;
    height: 26px;
    padding: 2px;

    border: 0;
    background: transparent;

    cursor: pointer;
}

.rating-info-button img {
    width: 16px;
    height: 16px;
    object-fit: contain;
}

.rating-person-marks {
    display: flex;
    flex: 0 0 auto;
    gap: 4px;

    max-width: 55%;
    overflow-x: auto;

    scrollbar-width: none;
}

.rating-person-marks::-webkit-scrollbar {
    display: none;
}

@keyframes rating-loader {
    to {
        transform: rotate(360deg);
    }
}
</style>
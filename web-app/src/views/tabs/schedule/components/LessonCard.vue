<template>
    <article
        class="schedule-lesson"
        :class="{
            'schedule-lesson-extra': lesson.isExtra,
        }"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="cancelLongPress"
        @contextmenu.prevent
    >
        <div class="lesson-main">
            <div class="lesson-heading">
                <span
                    v-if="!lesson.isExtra"
                    class="lesson-number"
                >
                    {{ strings.lessonNumber(number) }}
                </span>

                <span class="lesson-subject">
                    {{ lesson.subject }}
                </span>

                <div class="lesson-meta">
                    <span class="lesson-time">
                        {{ lesson.hours.string }}
                    </span>

                    <span
                        v-if="lesson.place"
                        class="lesson-place"
                    >
                        {{ lesson.place }}
                    </span>
                </div>

                <div
                    v-if="lesson.logs.length > 0"
                    class="lesson-marks"
                >
                    <MarkBadge
                        v-for="(mark, index) in lesson.logs"
                        :key="index"
                        :mark="mark"
                        size="lesson"
                        interactive
                        :disabled="!props.interactive || !canOpenRating"
                        @click="onRatingClick"
                    />
                </div>

                <div
                    v-if="showPraise"
                    class="lesson-actions"
                >
                    <button
                        class="lesson-praise"
                        type="button"
                        aria-label="Похвала"
                        :disabled="praiseLoading"
                        @click="onPraiseClick"
                    >
                        <span
                            v-if="praiseLoading"
                            class="lesson-loader"
                        ></span>

                        <span
                            v-else-if="praiseError"
                            class="lesson-error"
                        >
                            ×
                        </span>

                        <span
                            v-else
                            class="lesson-praise-icon"
                        >
                            👍
                        </span>
                    </button>
                </div>
            </div>

            <div
                v-if="!lesson.isExtra && lesson.works.length"
                class="lesson-works"
            >
                <p
                    v-for="(work, index) in lesson.works"
                    :key="index"
                    class="lesson-work-type"
                >
                    {{ work.title }}
                </p>
            </div>

            <div
                v-if="!lesson.isExtra && homeworkParts.length"
                class="lesson-homework-group"
            >
                <span class="lesson-emoji">
                    {{ homeworkEmoji }}
                </span>

                <p class="lesson-homework swiper-no-swiping">
                    <template
                        v-for="(part, index) in homeworkParts"
                        :key="index"
                    >
                        <a
                            v-if="part.type === 'link'"
                            :href="part.value"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="lesson-homework-link"
                        >
                            {{ part.value }}
                        </a>

                        <span v-else>{{ part.value }}</span>
                    </template>
                </p>
            </div>

            <div
                v-if="!lesson.isExtra && lesson.note?.text"
                class="lesson-note-group"
            >
                <span class="lesson-emoji">
                    {{ noteEmoji }}
                </span>

                <p class="lesson-note swiper-no-swiping">
                    {{ lesson.note.text }}
                </p>
            </div>

            <div
                v-if="!lesson.isExtra && props.showFiles && lesson.files.length"
                class="lesson-files"
            >
                <div
                    v-for="(file, index) in lesson.files"
                    :key="index"
                    class="lesson-file"
                >
                    <span class="lesson-file-emoji">
                        {{ strings.homeworkDocumentEmoji }}
                    </span>

                    <a
                        class="lesson-file-name"
                        :href="file.downloadUrl"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {{ file.fileName || strings.homeworkDocumentNotFound }}
                    </a>
                </div>
            </div>
        </div>

        <svg
            v-if="isLongPressing"
            class="lesson-long-press-border"
            aria-hidden="true"
        >
            <rect
                class="lesson-long-press-path"
                x="1"
                y="1"
                width="calc(100% - 2px)"
                height="calc(100% - 2px)"
                rx="14"
                pathLength="1"
                vector-effect="non-scaling-stroke"
                @animationend="onLongPressAnimationEnd"
            />
        </svg>
    </article>
</template>

<script setup lang="ts">
import {
    computed,
    ref,
} from "vue";

import { isLoadError } from "@/ui-core/state-utils";

import { strings } from "@/constants/strings";

import type {
    UiScheduleLesson,
} from "../types";

import type { ConfettiOptions } from "@/utils/confetti/confetti-engine";

import MarkBadge from "@/components/MarkBadge.vue";

const props = withDefaults(
    defineProps<{
        lesson: UiScheduleLesson;
        number: number;
        interactive?: boolean;
        showPraiseAction?: boolean;
        showFiles?: boolean;
        menuEnabled?: boolean;
    }>(),
    {
        interactive: true,
        showPraiseAction: true,
        showFiles: true,
        menuEnabled: true,
    },
);

const emit = defineEmits<{
    praise: [lessonKey: string, confettiOptions: ConfettiOptions];
    rating: [lessonKey: string];
    menu: [lessonKey: string];
}>();

const LONG_PRESS_DURATION = 300;
const LONG_PRESS_MOVE_LIMIT = 10;

const isLongPressing = ref(false);

let longPressPointerId: number | null = null;
let longPressStartX = 0;
let longPressStartY = 0;

function onPointerDown(event: PointerEvent): void {
    if (
        !props.interactive ||
        !props.menuEnabled ||
        props.lesson.isExtra ||
        !props.lesson.lessonKey ||
        event.button !== 0
    ) {
        return;
    }

    const target = event.target;

    if (
        target instanceof Element &&
        target.closest(
            "button, a, input, textarea, select, label",
        )
    ) {
        return;
    }

    longPressPointerId = event.pointerId;
    longPressStartX = event.clientX;
    longPressStartY = event.clientY;

    isLongPressing.value = true;

    const currentTarget = event.currentTarget;

    if (
        currentTarget instanceof HTMLElement &&
        currentTarget.hasPointerCapture(event.pointerId) === false
    ) {
        currentTarget.setPointerCapture(event.pointerId);
    }
}

function onPointerMove(event: PointerEvent): void {
    if (longPressPointerId !== event.pointerId) {
        return;
    }

    const deltaX = event.clientX - longPressStartX;
    const deltaY = event.clientY - longPressStartY;

    if (
        Math.hypot(deltaX, deltaY) > LONG_PRESS_MOVE_LIMIT
    ) {
        cancelLongPress();
    }
}

function onPointerUp(event: PointerEvent): void {
    if (longPressPointerId === event.pointerId) {
        cancelLongPress();
    }
}

function cancelLongPress(): void {
    longPressPointerId = null;
    isLongPressing.value = false;
}

function onLongPressAnimationEnd(): void {
    const lessonKey = props.lesson.lessonKey;

    if (
        longPressPointerId === null ||
        !lessonKey ||
        !isLongPressing.value
    ) {
        return;
    }

    cancelLongPress();
    emit("menu", lessonKey);
}

interface HomeworkPart {
    type: "text" | "link";
    value: string;
}

/**
 * Разбиваем текст домашнего задания на текстовые фрагменты
 * и HTTP(S)-ссылки.
 */
function parseHomework(text: string): HomeworkPart[] {
    const result: HomeworkPart[] = [];
    const pattern = /https?:\/\/[^\s<>"']+/gi;

    let cursor = 0;
    let match: RegExpExecArray | null;

    while ((match = pattern.exec(text)) !== null) {
        const rawUrl = match[0];
        const url = rawUrl.replace(/[),.!?;:]+$/, "");
        const suffix = rawUrl.slice(url.length);

        if (match.index > cursor) {
            result.push({
                type: "text",
                value: text.slice(cursor, match.index),
            });
        }

        if (url) {
            result.push({
                type: "link",
                value: url,
            });
        }

        if (suffix) {
            result.push({
                type: "text",
                value: suffix,
            });
        }

        cursor = match.index + rawUrl.length;
    }

    if (cursor < text.length) {
        result.push({
            type: "text",
            value: text.slice(cursor),
        });
    }

    return result;
}

const homeworkParts = computed(() => {
    const homework = props.lesson.homework;

    if (!homework?.trim()) {
        return [];
    }

    return parseHomework(homework);
});

const showPraise = computed(() =>
    props.showPraiseAction &&
    !props.lesson.isExtra &&
    props.lesson.lessonKey !== null &&
    props.lesson.praiseState !== null &&
    props.lesson.logs.length > 0 &&
    props.lesson.praiseState.type !== "success",
);

const canOpenRating = computed(() =>
    !props.lesson.isExtra &&
    props.lesson.lessonKey !== null &&
    props.lesson.ratingKey !== null,
);

const praiseLoading = computed(
    () => props.lesson.praiseState?.type === "loading",
);

const praiseError = computed(
    () => isLoadError(props.lesson.praiseState),
);

function onPraiseClick(event: MouseEvent): void {
    const lessonKey = props.lesson.lessonKey;

    if (
        !props.interactive ||
        !lessonKey ||
        praiseLoading.value
    ) {
        return;
    }

    const rect = (
        event.currentTarget as HTMLElement
    ).getBoundingClientRect();
    const confettiOptions = {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
    };

    emit("praise", lessonKey, confettiOptions);
}

function onRatingClick(): void {
    const lessonKey = props.lesson.lessonKey;

    if (
        !props.interactive ||
        !canOpenRating.value ||
        !lessonKey
    ) {
        return;
    }

    emit("rating", lessonKey);
}

const homeworkEmoji = strings.homeworkEmoji;
const noteEmoji = strings.noteEmoji;
const homeworkDocumentEmoji = strings.homeworkDocumentEmoji;
</script>

<style scoped>
.schedule-lesson {
    display: flex;
    align-items: flex-start;

    width: 100%;
    min-width: 0;

    margin-bottom: 8px;
    padding: 12px;

    border: 1px solid var(--stroke-bg);
    border-radius: 15px;

    background: var(--lesson-bg);
    color: var(--lesson-subject);
}

.schedule-lesson {
    position: relative;
}

.lesson-long-press-border {
    position: absolute;
    inset: 0;
    z-index: 3;

    width: 100%;
    height: 100%;

    overflow: visible;

    pointer-events: none;
}

.lesson-long-press-path {
    fill: none;
    stroke: #fff;
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;

    stroke-dasharray: 1;
    stroke-dashoffset: 1;

    animation: lesson-long-press 300ms linear forwards;
}

@keyframes lesson-long-press {
    to {
        stroke-dashoffset: 0;
    }
}

.schedule-lesson-extra {
    background: var(--lesson-bg-extra);
}

.lesson-main {
    flex: 1;
    min-width: 0;
}

.lesson-heading {
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;

    column-gap: 8px;
    row-gap: 4px;

    font-family: sans-serif;
}

.lesson-number,
.lesson-subject {
    font-size: 18px;
    font-weight: 500;
}

.lesson-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;

    gap: 2px 10px;
}

.lesson-time {
    color: var(--lesson-time);
    font-size: 14px;
    font-weight: 500;
}

.lesson-place {
    color: var(--lesson-place);
    font-size: 14px;
}

.lesson-marks {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;
    margin-left: auto;
}

.lesson-works {
    margin-top: 2px;
}

.lesson-work-type {
    margin: 2px 0 0;

    color: var(--lesson-work-type);
    font-size: 14px;

    overflow-wrap: anywhere;
}

.lesson-homework-group,
.lesson-note-group {
    display: flex;
    align-items: flex-start;
    gap: 5px;

    margin-top: 6px;
}

.lesson-emoji {
    flex: 0 0 auto;
    font-size: 14px;
}

.lesson-homework,
.lesson-note {
    min-width: 0;
    margin: 0;

    font-size: 14px;
    line-height: 1.4;

    overflow-wrap: anywhere;
    white-space: pre-wrap;
}

.lesson-homework {
    color: var(--lesson-homework-text);
}

.lesson-homework-link {
    color: var(--lesson-link);
    text-decoration: underline;
    overflow-wrap: anywhere;
}

.lesson-note {
    color: var(--lesson-note-text);
}

.lesson-files {
    display: flex;
    flex-direction: column;
    gap: 2px;

    margin-top: 6px;
}

.lesson-file {
    display: flex;
    align-items: flex-start;
    gap: 5px;

    min-width: 0;

    font-size: 14px;
    line-height: 1.4;
}

.lesson-file-name {
    min-width: 0;
    overflow-wrap: anywhere;

    color: var(--lesson-homework-file-name);
}

.lesson-actions {
    display: flex;
    flex: 0 0 auto;
    align-items: flex-start;
}

.lesson-praise {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    width: 34px;
    height: 34px;

    padding: 0;

    border: 1px solid var(--stroke-bg);
    border-radius: 50%;

    background: var(--button-bg);
    color: var(--lesson-like-icon);

    font-size: 23px;
    line-height: 1;

    cursor: pointer;
}

.lesson-loader {
    display: inline-block;

    width: 16px;
    height: 16px;

    border: 2px solid var(--stroke-bg);
    border-top-color: var(--slider-accent);
    border-radius: 50%;

    animation: lesson-loader 0.7s linear infinite;
}

.lesson-error {
    color: #e53935;
    font-size: 25px;
}

.lesson-praise-icon {
    line-height: 1;
}

.lesson-subject-button {
    padding: 0;

    border: 0;
    background: transparent;
    color: inherit;

    font: inherit;
    text-align: left;

    cursor: pointer;
}

.lesson-subject-button:disabled {
    cursor: default;
}

.lesson-mark:disabled {
    cursor: default;
}

@keyframes lesson-loader {
    to {
        transform: rotate(360deg);
    }
}
</style>
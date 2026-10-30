<template>
    <article
        class="schedule-lesson"
        :class="{
            'schedule-lesson-extra': lesson.isExtra,
        }"
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
                    <div
                        v-for="(mark, index) in lesson.logs"
                        :key="index"
                        class="lesson-mark"
                        :class="getMarkMoodClass(mark.mood)"
                    >
                        {{ mark.value }}
                    </div>
                </div>

                <div
                    v-if="showPraise"
                    class="lesson-actions"
                >
                    <button
                        class="lesson-praise"
                        type="button"
                        aria-label="Похвала"
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
                v-if="!lesson.isExtra && lesson.files.length"
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
    </article>
</template>

<script setup lang="ts">
import {
    computed,
} from "vue";

import { strings } from "@/constants/strings";

import type {
    UiScheduleLesson,
} from "../types";

const props = defineProps<{
    lesson: UiScheduleLesson;
    number: number;
}>();

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
    !props.lesson.isExtra &&
    props.lesson.praiseState !== null &&
    props.lesson.logs.length > 0 &&
    props.lesson.praiseState.type !== "success",
);

const praiseLoading = computed(
    () => props.lesson.praiseState?.type === "loading",
);

const praiseError = computed(
    () => props.lesson.praiseState?.type === "error",
);

const homeworkEmoji = strings.homeworkEmoji;
const noteEmoji = strings.noteEmoji;
const homeworkDocumentEmoji = strings.homeworkDocumentEmoji;

function getMarkMoodClass(mood: string): string {
    switch (mood) {
        case "good":
            return "lesson-mark-good";

        case "average":
            return "lesson-mark-average";

        case "bad":
            return "lesson-mark-bad";

        case "more":
        default:
            return "lesson-mark-more";
    }
}
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

.lesson-mark {
    display: flex;
    align-items: center;
    justify-content: center;

    min-width: 32px;
    height: 32px;
    padding: 4px;

    border: 1px solid var(--mark-log-bg);
    border-radius: 5px;
    background: var(--mark-log-bg);

    color: #fff;
    font-size: 20px;
    font-family: sans-serif;
    font-weight: 500;
    line-height: 1;

    cursor: pointer;
}

.lesson-mark-good {
    background: var(--mark-log-good);
}

.lesson-mark-average {
    background: var(--mark-log-average);
}

.lesson-mark-bad {
    background: var(--mark-log-bad);
}

.lesson-mark-more {
    background: var(--mark-log-more);
}

.lesson-mark:active {
    background: var(--mark-log-pressed);
}

.lesson-mark {
    position: relative;
    isolation: isolate;
}

.lesson-mark:active::after {
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: var(--mark-log-pressed);
    content: "";
    pointer-events: none;
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

@keyframes lesson-loader {
    to {
        transform: rotate(360deg);
    }
}
</style>
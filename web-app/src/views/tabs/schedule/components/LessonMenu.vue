<template>
    <Transition
        name="lesson-menu"
        @after-leave="onAfterLeave"
    >
        <div
            v-if="modelValue"
            class="lesson-menu-overlay"
            role="dialog"
            aria-modal="true"
            @click.self="close"
            @keydown.esc.stop.prevent="close"
        >
            <div class="lesson-menu-content">
                <LessonCard
                    :lesson="lesson"
                    :number="lesson.number + 1"
                    :interactive="false"
                    :show-praise-action="false"
                    :show-files="false"
                    :menu-enabled="false"
                />

                <div class="lesson-menu-actions">
                    <button
                        v-if="!hasNote"
                        class="lesson-menu-item"
                        type="button"
                        @click="selectAction('note')"
                    >
                        <span class="lesson-menu-icon">
                            {{ strings.noteEmoji }}
                        </span>
                        <span>{{ strings.lessonNoteAdd }}</span>
                    </button>

                    <template v-else>
                        <button
                            class="lesson-menu-item"
                            type="button"
                            @click="selectAction('note')"
                        >
                            <span class="lesson-menu-icon">
                                {{ strings.noteEmoji }}
                            </span>
                            <span>{{ strings.lessonNoteEdit }}</span>
                        </button>

                        <button
                            class="lesson-menu-item"
                            type="button"
                            @click="selectAction('delete-note')"
                        >
                            <span class="lesson-menu-icon">🗑️</span>
                            <span>{{ strings.lessonNoteDelete }}</span>
                        </button>
                    </template>

                    <button
                        v-if="canPraise"
                        class="lesson-menu-item"
                        type="button"
                        @click="selectAction('praise')"
                    >
                        <span class="lesson-menu-icon">👍</span>
                        <span>{{ strings.sendPraise }}</span>
                    </button>

                    <button
                        v-if="canOpenRating"
                        class="lesson-menu-item"
                        type="button"
                        @click="selectAction('rating')"
                    >
                        <span class="lesson-menu-icon">⭐</span>
                        <span>{{ strings.openRating }}</span>
                    </button>

                    <button
                        class="lesson-menu-item"
                        type="button"
                        :disabled="!lesson.dnevnikruUrl"
                        @click="selectAction('dnevnik')"
                    >
                        <img
                            class="lesson-menu-icon"
                            :src="`${routes.home}icons/dnevnik_ru.svg`"
                        />
                        <span>{{ strings.openLessonDnevnikru }}</span>
                    </button>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import { strings } from "@/constants/strings";
import { routes } from "@/constants/routes";

import LessonCard from "./LessonCard.vue";

import type { UiScheduleLesson } from "../types";

type LessonMenuAction =
    | "note"
    | "delete-note"
    | "praise"
    | "rating"
    | "dnevnik";

const props = defineProps<{
    modelValue: boolean;
    lesson: UiScheduleLesson;
}>();

const emit = defineEmits<{
    "update:modelValue": [value: boolean];
    note: [];
    "delete-note": [];
    praise: [];
    rating: [];
    dnevnik: [];
}>();

const pendingAction = ref<LessonMenuAction | null>(null);

const hasNote = computed(
    () => Boolean(props.lesson.note?.text.trim()),
);

const canPraise = computed(
    () =>
        props.lesson.praiseState?.type === "empty" &&
        props.lesson.logs.length > 0,
);

const canOpenRating = computed(
    () =>
        Boolean(props.lesson.ratingKey) &&
        (
            props.lesson.logs.length > 0 ||
            props.lesson.othersMarks.length > 0
        ),
);

function close(): void {
    pendingAction.value = null;
    emit("update:modelValue", false);
}

function selectAction(action: LessonMenuAction): void {
    pendingAction.value = action;
    emit("update:modelValue", false);
}

function onAfterLeave(): void {
    const action = pendingAction.value;

    pendingAction.value = null;

    switch (action) {
        case "note":
            emit("note");
            break;

        case "delete-note":
            emit("delete-note");
            break;

        case "praise":
            emit("praise");
            break;

        case "rating":
            emit("rating");
            break;

        case "dnevnik":
            emit("dnevnik");
            break;
    }
}
</script>

<style scoped>
.lesson-menu-overlay {
    position: fixed;
    inset: 0;
    z-index: 1050;

    box-sizing: border-box;
    overflow-y: auto;

    padding: 1px 16px 24px;

    background: var(--dialog-menu-background);
}

.lesson-menu-content {
    width: 100%;
    max-width: 720px;

    margin: 99px auto 0;
}

.lesson-menu-actions {
    display: flex;
    flex-direction: column;

    width: fit-content;
    min-width: 250px;
    max-width: 100%;

    margin: 14px 0 0 auto;

    overflow: hidden;

    border: 1px solid var(--stroke-bg);
    border-radius: 15px;

    background: var(--lesson-bg);
    color: var(--text-primary);
}

.lesson-menu-item {
    display: flex;
    align-items: center;
    gap: 15px;

    width: 100%;
    min-height: 48px;
    padding: 10px;

    border: 0;
    background: transparent;
    color: inherit;

    font: inherit;
    font-size: 16px;
    font-weight: 600;
    text-align: left;

    cursor: pointer;
}

.lesson-menu-item:active {
    background: var(--mark-log-pressed);
}

.lesson-menu-item:disabled {
    opacity: 0.45;
    cursor: default;
}

.lesson-menu-icon {
    display: inline-flex;
    flex: 0 0 18px;
    align-items: center;
    justify-content: center;

    width: 18px;
    height: 18px;

    font-size: 18px;
    line-height: 1;
}

.lesson-menu-enter-active .lesson-menu-content,
.lesson-menu-leave-active .lesson-menu-content {
    transition:
        opacity 220ms ease,
        transform 220ms ease;
}

.lesson-menu-enter-active {
    transition: background-color 180ms ease;
}

.lesson-menu-leave-active {
    transition: background-color 160ms ease;
}

.lesson-menu-enter-from,
.lesson-menu-leave-to {
    background-color: transparent;
}

.lesson-menu-enter-from .lesson-menu-content,
.lesson-menu-leave-to .lesson-menu-content {
    opacity: 0;
    transform: translateY(30px);
}
</style>
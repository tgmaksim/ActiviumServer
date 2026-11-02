<template>
    <div
        v-if="visible"
        class="note-editor-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="note-editor-title"
        @click.self="close"
        @keydown.esc.stop.prevent="close"
    >
        <form
            class="note-editor-dialog"
            @submit.prevent="submit"
        >
            <h2
                id="note-editor-title"
                class="note-editor-title"
            >
                {{
                    editing
                        ? strings.titleDialogEditNote
                        : strings.titleDialogCreateNote
                }}
            </h2>

            <textarea
                v-model="text"
                class="note-editor-input"
                :placeholder="strings.messageDialogCreateNote"
                :maxlength="TEXT_LIMIT"
                rows="6"
            ></textarea>

            <p
                class="note-editor-counter"
                :class="{
                    'note-editor-counter-limit':
                        text.length === TEXT_LIMIT,
                }"
            >
                {{ strings.praiseTextCounter(text.length, TEXT_LIMIT) }}
            </p>

            <label class="note-editor-public">
                <input
                    v-model="isPublic"
                    type="checkbox"
                >

                <span>{{ strings.switchPublicNote }}</span>
            </label>

            <div class="note-editor-reminder">
                <label
                    class="note-editor-reminder-label"
                    for="note-reminder"
                >
                    {{ strings.noteRemindIn }}
                </label>

                <div class="note-editor-reminder-controls">
                    <input
                        id="note-reminder"
                        v-model="remindDateTime"
                        class="note-editor-datetime"
                        type="datetime-local"
                        step="60"
                    >

                    <button
                        v-if="remindDateTime"
                        class="note-editor-clear-reminder"
                        type="button"
                        @click="remindDateTime = ''"
                    >
                        ×
                    </button>
                </div>
            </div>

            <div class="note-editor-actions">
                <button
                    class="note-editor-cancel"
                    type="button"
                    @click="close"
                >
                    {{ strings.cancel }}
                </button>

                <button
                    class="note-editor-submit"
                    type="submit"
                >
                    {{ strings.buttonDialogCreateNote }}
                </button>
            </div>
        </form>

        <AppDialog
            :visible="showEmptyNoteDialog"
            :title="strings.titleDialogNoNoteText"
            :message="strings.messageDialogNoNoteText"
            :action-text="strings.buttonDialogNoNoteText"
            @action="showEmptyNoteDialog = false"
            @cancel="showEmptyNoteDialog = false"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

import AppDialog from "@/components/AppDialog.vue";

import { strings } from "@/constants/strings";

import type { Note } from "@/api/dtools";

const TEXT_LIMIT = 256;

const props = defineProps<{
    visible: boolean;
    note: Note | null;
    timezone: number;
}>();

const emit = defineEmits<{
    close: [];
    submit: [
        data: {
            text: string;
            public: boolean;
            remindTime: string | null;
        },
    ];
}>();

const text = ref("");
const isPublic = ref(true);
const remindDateTime = ref("");
const showEmptyNoteDialog = ref(false);

const editing = ref(false);

watch(
    () => [
        props.visible,
        props.note,
        props.timezone,
    ] as const,
    ([visible, note, timezone]) => {
        if (!visible) {
            showEmptyNoteDialog.value = false;
            return;
        }

        editing.value = Boolean(note?.text.trim());

        text.value = note?.text ?? "";
        isPublic.value = note?.public ?? true;

        remindDateTime.value = note?.remindTime
            ? toDateTimeLocal(note.remindTime, timezone)
            : "";

        showEmptyNoteDialog.value = false;
    },
    { immediate: true },
);

/**
 * Преобразует ISO-время в значение datetime-local
 * с учётом часового пояса расписания.
 */
function toDateTimeLocal(
    value: string,
    timezone: number,
): string {
    const timestamp = Date.parse(value);

    if (!Number.isFinite(timestamp)) {
        return "";
    }

    const date = new Date(timestamp + timezone * 1000);

    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    const hours = String(date.getUTCHours()).padStart(2, "0");
    const minutes = String(date.getUTCMinutes()).padStart(2, "0");

    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Преобразует datetime-local в ISO-время.
 * Значение хранится как абсолютный момент времени,
 * а не как локальное время браузера.
 */
function toIsoDateTime(
    value: string,
    timezone: number,
): string | null {
    if (!value) {
        return null;
    }

    const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(value);

    if (!match) {
        return null;
    }

    const [
        ,
        year,
        month,
        day,
        hours,
        minutes,
    ] = match;

    const timestamp = Date.UTC(
        Number(year),
        Number(month) - 1,
        Number(day),
        Number(hours),
        Number(minutes),
    ) - timezone * 1000;

    const date = new Date(timestamp);

    if (!Number.isFinite(date.getTime())) {
        return null;
    }

    return date.toISOString();
}

function close(): void {
    showEmptyNoteDialog.value = false;
    emit("close");
}

function submit(): void {
    const normalizedText = text.value.trim();

    if (!normalizedText) {
        showEmptyNoteDialog.value = true;
        return;
    }

    emit("submit", {
        text: normalizedText,
        public: isPublic.value,
        remindTime: toIsoDateTime(
            remindDateTime.value,
            props.timezone,
        ),
    });

    emit("close");
}
</script>

<style scoped>
.note-editor-overlay {
    position: fixed;
    inset: 0;
    z-index: 1100;

    display: flex;
    align-items: center;
    justify-content: center;

    box-sizing: border-box;
    padding: 20px;
    overflow-y: auto;

    background: rgb(0 0 0 / 40%);
}

.note-editor-dialog {
    box-sizing: border-box;

    width: min(100%, 400px);
    max-height: calc(100dvh - 40px);
    overflow-y: auto;

    padding: 24px;

    border-radius: 20px;

    background: var(--main-bg);
    color: var(--text-primary);

    box-shadow: 0 10px 40px rgb(0 0 0 / 20%);
}

.note-editor-title {
    margin: 0 0 16px;

    font-size: 20px;
    line-height: 1.3;
}

.note-editor-input {
    display: block;
    box-sizing: border-box;

    width: 100%;
    min-height: 120px;
    padding: 12px;

    border: 1px solid var(--stroke-bg);
    border-radius: 12px;

    background: var(--main-bg);
    color: var(--text-primary);

    font: inherit;
    line-height: 1.5;

    resize: vertical;
}

.note-editor-input::placeholder {
    color: var(--text-secondary);
    opacity: 1;
}

.note-editor-counter {
    margin: 8px 0 16px;

    color: var(--text-secondary);
    font-size: 13px;
    text-align: right;
}

.note-editor-counter-limit {
    color: var(--dialog-button-negative);
}

.note-editor-public {
    display: flex;
    align-items: center;
    gap: 10px;

    margin: 16px 0;

    font-size: 14px;
}

.note-editor-public input {
    width: 18px;
    height: 18px;

    accent-color: var(--slider-accent);
}

.note-editor-reminder {
    display: flex;
    flex-direction: column;
    gap: 8px;

    margin: 16px 0;
}

.note-editor-reminder-label {
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 600;
}

.note-editor-reminder-controls {
    display: flex;
    align-items: center;
    gap: 8px;
}

.note-editor-datetime {
    box-sizing: border-box;
    flex: 1;
    min-width: 0;
    min-height: 42px;
    padding: 8px 10px;

    border: 1px solid var(--stroke-bg);
    border-radius: 10px;

    background: var(--main-bg);
    color: var(--text-primary);

    font: inherit;
}

.note-editor-clear-reminder {
    width: 36px;
    height: 36px;

    border: 0;
    border-radius: 50%;

    background: var(--dialog-background);
    color: var(--dialog-button-negative);

    font-size: 24px;
    line-height: 1;

    cursor: pointer;
}

.note-editor-actions {
    display: flex;
    gap: 10px;

    margin-top: 20px;
}

.note-editor-submit,
.note-editor-cancel {
    flex: 1;
    min-width: 0;
    min-height: 44px;
    padding: 10px 16px;

    border: 0;
    border-radius: 12px;

    background: var(--dialog-background);

    font: inherit;
    font-weight: 600;

    cursor: pointer;
}

.note-editor-submit {
    color: var(--dialog-button-positive);
}

.note-editor-cancel {
    color: var(--dialog-button-negative);
}

.note-editor-submit:active,
.note-editor-cancel:active {
    opacity: 0.8;
}
</style>
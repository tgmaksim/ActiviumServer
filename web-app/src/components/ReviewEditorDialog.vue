<template>
    <div
        v-if="visible"
        class="dialog-overlay"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        @click.self="close"
    >
        <div class="dialog">
            <h2
                :id="titleId"
                class="dialog-title"
            >
                {{
                    editing
                        ? strings.reviewEditorEditTitle
                        : strings.reviewEditorNewTitle
                }}
            </h2>

            <div
                class="review-stars"
                role="group"
                :aria-label="strings.reviewEditorNewTitle"
            >
                <button
                    v-for="star in 5"
                    :key="star"
                    class="star-button"
                    :class="{
                        'star-selected': star <= selectedStars,
                    }"
                    type="button"
                    :aria-label="String(star)"
                    :aria-pressed="star === selectedStars"
                    @click="selectedStars = star"
                >
                    {{ star <= selectedStars ? "★" : "☆" }}
                </button>
            </div>

            <textarea
                v-model="text"
                class="review-input"
                :placeholder="strings.reviewTextHint"
                :maxlength="TEXT_LIMIT"
                rows="5"
            ></textarea>

            <p
                class="text-counter"
                :class="{
                    'text-counter-limit': text.length === TEXT_LIMIT,
                }"
            >
                {{ strings.reviewTextCounter(text.length, TEXT_LIMIT) }}
            </p>

            <div class="dialog-actions">
                <button
                    class="dialog-cancel"
                    type="button"
                    @click="close"
                >
                    {{ strings.ok }}
                </button>

                <button
                    class="dialog-action"
                    type="button"
                    @click="submit"
                >
                    {{ strings.send }}
                </button>
            </div>
        </div>

        <AppDialog
            :visible="showStarsError"
            :title="strings.titleDialogReviewNoStars"
            :message="strings.messageDialogReviewNoStars"
            :action-text="strings.buttonDialogReviewNoStars"
            @action="showStarsError = false"
            @cancel="showStarsError = false"
        />
    </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import AppDialog from "@/components/AppDialog.vue";
import { strings } from "@/constants/strings";

const TEXT_LIMIT = 512;

const props = defineProps<{
    visible: boolean;
    editing: boolean;
    initialStars?: number;
    initialText?: string;
}>();

const emit = defineEmits<{
    close: [];
    submit: [review: { stars: number; text: string | null }];
}>();

const titleId = "review-editor-title";

const selectedStars = ref(0);
const text = ref("");
const showStarsError = ref(false);

watch(
    () => [
        props.visible,
        props.editing,
        props.initialStars,
        props.initialText,
    ] as const,
    ([visible, editing, initialStars, initialText]) => {
        if (!visible) {
            showStarsError.value = false;
            return;
        }

        selectedStars.value = editing ? initialStars ?? 0 : 0;
        text.value = editing ? initialText ?? "" : "";
        showStarsError.value = false;
    },
    { immediate: true },
);

const normalizedText = computed(
    () => text.value.trim() || null,
);

function close(): void {
    if (showStarsError.value) {
        showStarsError.value = false;
    }

    emit("close");
}

function submit(): void {
    if (selectedStars.value < 1 || selectedStars.value > 5) {
        showStarsError.value = true;
        return;
    }

    emit("close");

    emit("submit", {
        stars: selectedStars.value,
        text: normalizedText.value,
    });
}
</script>

<style scoped>
.dialog-overlay {
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

.dialog {
    box-sizing: border-box;
    width: min(100%, 400px);
    max-height: calc(100dvh - 40px);
    overflow-y: auto;

    padding: 24px;
    border-radius: 20px;

    background: var(--dialog-background);
    color: var(--text-primary);

    box-shadow: 0 10px 40px rgb(0 0 0 / 20%);
}

.dialog-title {
    margin: 0 0 16px;
    font-size: 20px;
    line-height: 1.3;
}

.review-stars {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 16px;
}

.star-button {
    min-width: 40px;
    min-height: 44px;
    padding: 0;

    border: 0;
    background: transparent;
    color: var(--text-secondary);

    font-size: 34px;
    line-height: 1;

    cursor: pointer;
}

.star-button.star-selected {
    color: var(--slider-accent);
}

.review-input {
    display: block;
    box-sizing: border-box;
    width: 100%;
    min-height: 120px;
    padding: 12px;

    border: 1px solid var(--stroke-bg);
    border-radius: 12px;

    background: var(--dialog-background);
    color: var(--text-primary);

    font: inherit;
    line-height: 1.5;
    resize: vertical;
}

.review-input::placeholder {
    color: var(--text-secondary);
    opacity: 1;
}

.text-counter {
    margin: 8px 0 16px;
    color: var(--text-secondary);
    font-size: 13px;
    text-align: right;
}

.text-counter-limit {
    color: var(--dialog-button-negative);
}

.dialog-actions {
    display: flex;
    gap: 10px;
}

.dialog-action,
.dialog-cancel {
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

.dialog-action {
    color: var(--dialog-button-positive);
}

.dialog-cancel {
    color: var(--dialog-button-negative);
}

.dialog-action:active,
.dialog-cancel:active {
    opacity: 0.8;
}
</style>

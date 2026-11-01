<template>
    <div
        v-if="visible"
        class="dialog-overlay"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        @click.self="close"
        @keydown.esc.stop.prevent="close"
    >
        <div class="dialog">
            <h2
                :id="titleId"
                class="dialog-title"
            >
                {{ strings.sendPraise }}
            </h2>

            <textarea
                v-model="text"
                class="review-input"
                :placeholder="strings.messageDialogSendPraise"
                rows="5"
            ></textarea>

            <p
                class="text-counter"
                :class="{
                    'text-counter-limit': text.length > TEXT_LIMIT,
                }"
            >
                {{ text.length }}/{{ TEXT_LIMIT }}
            </p>

            <div class="dialog-actions">
                <button
                    class="dialog-cancel"
                    type="button"
                    @click="close"
                >
                    {{ strings.cancel }}
                </button>

                <button
                    class="dialog-action"
                    type="button"
                    @click="submit"
                >
                    {{ strings.sendPraise }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

import { strings } from "@/constants/strings";

const TEXT_LIMIT = 64;

const props = defineProps<{
    visible: boolean;
}>();

const emit = defineEmits<{
    close: [];
    submit: [text: string | null];
}>();

const titleId = "praise-dialog-title";

const text = ref("");

watch(
    () => props.visible,
    (visible) => {
        if (visible) {
            text.value = "";
        }
    },
);

function close(): void {
    emit("close");
}

function submit(): void {
    emit("close");
    emit("submit", text.value.trim() || null);
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

    background: var(--main-bg);
    color: var(--text-primary);

    box-shadow: 0 10px 40px rgb(0 0 0 / 20%);
}

.dialog-title {
    margin: 0 0 16px;
    font-size: 20px;
    line-height: 1.3;
}

.review-input {
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
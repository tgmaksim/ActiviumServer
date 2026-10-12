<template>
    <div
        v-if="visible"
        class="dialog-overlay"
        role="dialog"
        aria-modal="true"
    >
        <div class="dialog">
            <h2 v-if="title" class="dialog-title">
                {{ title }}
            </h2>

            <p v-if="message" class="dialog-message">
                {{ message }}
            </p>

            <div
                v-if="actionText || cancelText"
                class="dialog-actions"
            >
                <button
                    v-if="cancelText"
                    class="dialog-cancel"
                    type="button"
                    @click="$emit('cancel')"
                >
                    {{ cancelText }}
                </button>

                <button
                    v-if="actionText"
                    class="dialog-action"
                    type="button"
                    @click="$emit('action')"
                >
                    {{ actionText }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    visible: boolean;
    title?: string;
    message?: string;
    actionText?: string;
    cancelText?: string;
}>();

defineEmits<{
    action: [];
    cancel: [];
}>();
</script>

<style scoped>
.dialog-overlay {
    position: fixed;
    inset: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    padding: 20px;

    background: rgb(0 0 0 / 40%);
    z-index: 1000;
}

.dialog {
    width: min(100%, 400px);
    padding: 24px;

    border-radius: 20px;
    background: var(--dialog-background);
    color: var(--text-primary);

    box-shadow: 0 10px 40px rgb(0 0 0 / 20%);
}

.dialog-title {
    margin: 0 0 12px;
    font-size: 20px;
}

.dialog-message {
    margin: 0 0 10px;
    line-height: 1.5;
    white-space: pre-line;
}

.dialog-actions {
    display: flex;
    flex-direction: row;
    gap: 10px;
}

.dialog-action,
.dialog-cancel {
    width: 100%;
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
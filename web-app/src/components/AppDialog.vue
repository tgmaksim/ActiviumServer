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
</template>

<script setup lang="ts">
defineProps<{
    visible: boolean;
    title?: string;
    message?: string;
    actionText?: string;
}>();

defineEmits<{
    action: [];
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
    background: var(--color-surface, #ffffff);
    color: var(--color-text, #111111);

    box-shadow: 0 10px 40px rgb(0 0 0 / 20%);
}

.dialog-title {
    margin: 0 0 12px;
    font-size: 20px;
}

.dialog-message {
    margin: 0 0 20px;
    line-height: 1.5;
}

.dialog-action {
    width: 100%;
    min-height: 44px;

    border: 0;
    border-radius: 12px;

    background: #1683ff;
    color: #ffffff;

    font: inherit;
    font-weight: 600;

    cursor: pointer;
}

.dialog-action:active {
    opacity: 0.8;
}
</style>
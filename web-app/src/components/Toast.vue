<script setup lang="ts">
import { onBeforeUnmount, watch } from "vue";
import {
    currentToast,
    dismissToast,
    getToastDuration,
} from "../composables/useToast";

let timeoutId: ReturnType<typeof setTimeout> | undefined;

watch(
    currentToast,
    (toast) => {
        if (timeoutId !== undefined) {
            clearTimeout(timeoutId);
            timeoutId = undefined;
        }

        if (toast === null) {
            return;
        }

        const toastId = toast.id;

        timeoutId = setTimeout(() => {
            dismissToast(toastId);
            timeoutId = undefined;
        }, getToastDuration(toast.duration));
    },
    { immediate: true },
);

onBeforeUnmount(() => {
    if (timeoutId !== undefined) {
        clearTimeout(timeoutId);
    }
});
</script>

<template>
    <Transition name="toast">
        <div
            v-if="currentToast"
            class="toast"
            role="status"
            aria-live="polite"
        >
            {{ currentToast.message }}
        </div>
    </Transition>
</template>

<style scoped>
.toast {
    position: fixed;
    z-index: 1000;
    bottom: calc(90px + env(safe-area-inset-bottom, 0px));
    left: 50%;
    transform: translateX(-50%);

    width: max-content;
    max-width: calc(100% - 32px);
    box-sizing: border-box;

    padding: 12px 16px;
    border-radius: 14px;

    background: var(--bg-bottom-menu);
    color: var(--bottom-menu-icon-checked);
    border: 1px solid var(--slider-accent);

    font-size: 14px;
    line-height: 20px;
    overflow-wrap: anywhere;
    text-align: center;

    box-shadow: 0 4px 16px rgb(0 0 0 / 16%);
    pointer-events: none;
}
</style>

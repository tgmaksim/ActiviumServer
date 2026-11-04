<template>
    <button
        v-if="interactive"
        class="mark-badge"
        :class="[
            `mark-badge-${size}`,
            moodClass,
            { 'mark-badge-muted': !mark },
        ]"
        type="button"
        :disabled="disabled || !mark"
        @click="emit('click')"
    >
        {{ mark?.value ?? "—" }}
    </button>

    <span
        v-else
        class="mark-badge"
        :class="[
            `mark-badge-${size}`,
            moodClass,
            { 'mark-badge-muted': !mark },
        ]"
    >
        {{ mark?.value ?? "—" }}
    </span>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { MarkLog } from "@/api/dnevnik";

const props = withDefaults(
    defineProps<{
        mark: MarkLog | null;
        size?: "compact" | "lesson" | "large" | "rating";
        interactive?: boolean;
        disabled?: boolean;
    }>(),
    {
        size: "compact",
        interactive: false,
        disabled: false,
    },
);

const emit = defineEmits<{
    click: [];
}>();

const moodClass = computed(() => {
    switch (props.mark?.mood) {
        case "good":
            return "mark-badge-good";

        case "average":
            return "mark-badge-average";

        case "bad":
            return "mark-badge-bad";

        case "more":
        default:
            return "mark-badge-more";
    }
});
</script>

<style scoped>
.mark-badge {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    min-width: 17px;

    padding: 0 3px;

    border-radius: 5px;
    border: 0;

    background: var(--mark-log-bg);
    color: #FFFFFF;

    font-family: sans-serif;
    font-weight: 500;
    line-height: 1;

    white-space: nowrap;
    user-select: none;
    cursor: pointer;
}

.mark-badge-compact {
    height: 17px;

    margin-bottom: 3px;

    font-size: 11px;
}

.mark-badge-lesson {
    min-width: 32px;
    height: 32px;

    padding: 4px;

    font-size: 20px;

    cursor: pointer;
}

.mark-badge-large {
    width: 100%;
    height: 40px;

    border-radius: 7px;

    font-size: 22px;
    font-weight: bold;
}

.mark-badge-rating {
    min-width: 32px;
    height: 32px;

    padding: 4px;

    font-size: 20px;
}

.mark-badge-good {
    background: var(--mark-log-good);
}

.mark-badge-average {
    background: var(--mark-log-average);
}

.mark-badge-bad {
    background: var(--mark-log-bad);
}

.mark-badge-more {
    background: var(--mark-log-more);
}

.mark-badge-muted {
    opacity: 0.4;
}

button.mark-badge:active:not(:disabled) {
    background: var(--mark-log-pressed);
}

button.mark-badge:disabled {
    cursor: default;
}
</style>
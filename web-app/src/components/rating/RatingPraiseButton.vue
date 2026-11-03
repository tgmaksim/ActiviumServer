<template>
    <button
        class="rating-praise"
        type="button"
        :disabled="loading"
        :aria-label="strings.sendPraise"
        @click="emit('click', $event)"
    >
        <RatingLoader
            v-if="loading"
            size="small"
        />

        <span
            v-else-if="error"
            class="rating-praise-error"
        >
            ×
        </span>

        <span v-else>👍</span>
    </button>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { isLoadError } from "@/ui-core/state-utils";

import type { LoadState } from "@/ui-core/load-state";

import { strings } from "@/constants/strings";

import RatingLoader from "./RatingLoader.vue";

const props = defineProps<{
    state: LoadState<unknown>;
}>();

const emit = defineEmits<{
    click: [event: MouseEvent];
}>();

const loading = computed(
    () => props.state.type === "loading",
);

const error = computed(
    () => isLoadError(props.state),
);
</script>

<style scoped>
.rating-praise {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;

    width: 38px;
    height: 38px;
    margin-left: auto;

    border: 1px solid var(--stroke-bg);
    border-radius: 50%;

    background: var(--button-bg);
    color: var(--lesson-like-icon);

    font-size: 23px;
    line-height: 1;

    cursor: pointer;
}

.rating-praise:disabled {
    cursor: default;
}

.rating-praise-error {
    color: #e53935;
    font-size: 26px;
}
</style>
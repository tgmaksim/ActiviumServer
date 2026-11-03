<template>
    <button
        class="last-mark-card"
        type="button"
        :aria-label="strings.openRating"
        @click="emit('rating', mark)"
    >
        <MarkBadge
            :mark="mark.mark"
            size="large"
        />

        <div class="last-mark-subject">
            {{ mark.subject }}
        </div>

        <div class="last-mark-detail">
            {{ detail }}
        </div>
    </button>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { strings } from "@/constants/strings";

import MarkBadge from "@/components/MarkBadge.vue";

import type { MarkLast } from "@/api/dnevnik";

const props = defineProps<{
    mark: MarkLast;
}>();

const emit = defineEmits<{
    rating: [mark: MarkLast];
}>();

const detail = computed(() => {
    const work = props.mark.mark.work;
    const date = props.mark.humanLessonDate;

    if (!work) {
        return date
            ? strings.lastMarkDetailNoWork(date)
            : "";
    }

    if (!date) {
        return work.abbr;
    }

    return strings.lastMarkDetail(work.abbr, date);
});
</script>

<style scoped>
.last-mark-card {
    display: flex;
    flex: 0 0 90px;
    flex-direction: column;

    width: 90px;
    min-width: 0;

    padding: 4px;

    border: 0;
    background: transparent;
    color: inherit;

    text-align: left;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
}

.last-mark-card:active {
    opacity: 0.75;
}

.last-mark-subject {
    width: 100%;

    margin-top: 5px;

    color: var(--text-primary);
    font-size: 12px;

    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.last-mark-detail {
    color: var(--text-secondary);
    font-size: 11px;
    margin-top: 5px;

    overflow-wrap: anywhere;
}
</style>
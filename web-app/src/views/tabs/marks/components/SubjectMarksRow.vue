<template>
    <div
        v-if="mode === 'period'"
        class="subject-row subject-row-period"
    >
        <div class="subject-name">
            {{ subject }}
        </div>

        <div class="subject-marks">
            <MarkBadge
                v-for="(mark, index) in marks"
                :key="index"
                :mark="mark"
            />
        </div>

        <MarkBadge :mark="averageMark" />

        <MarkBadge :mark="periodMark" />
    </div>

    <div
        v-else
        class="subject-row subject-row-year"
    >
        <div class="subject-name">
            {{ subject }}
        </div>

        <div
            class="subject-year-marks"
            :style="{ '--period-count': Math.max(1, marks.length) }"
        >
            <MarkBadge
                v-for="(mark, index) in marks"
                :key="index"
                :mark="mark"
            />

            <MarkBadge
                v-if="marks.length === 0"
                :mark="null"
            />
        </div>

        <MarkBadge :mark="finalMark" />
    </div>
</template>

<script setup lang="ts">
import MarkBadge from "@/components/MarkBadge.vue";

import type { MarkLog } from "@/api/dnevnik";

withDefaults(
    defineProps<{
        subject: string;
        mode: "period" | "year";
        marks: readonly (MarkLog | null)[];
        averageMark?: MarkLog | null;
        periodMark?: MarkLog | null;
        finalMark?: MarkLog | null;
    }>(),
    {
        averageMark: null,
        periodMark: null,
        finalMark: null,
    },
);
</script>

<style scoped>
.subject-row {
    display: grid;
    align-items: start;

    width: 100%;
    min-width: 0;

    padding: 10px 8px;
}

.subject-row-period {
    grid-template-columns:
        minmax(78px, 1fr)
        minmax(0, 2fr)
        23px
        23px;

    column-gap: 5px;
}

.subject-row-year {
    grid-template-columns:
        minmax(78px, 1fr)
        minmax(0, 2fr)
        23px;

    column-gap: 5px;
}

.subject-name {
    min-width: 0;

    color: var(--text-primary);
    font-size: 13px;
    font-weight: 500;
    line-height: 1.3;

    white-space: normal;
    overflow-wrap: anywhere;
    hyphens: auto;
}

.subject-marks {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;

    gap: 2px;

    min-width: 0;
}

.subject-year-marks {
    display: grid;
    grid-template-columns:
        repeat(var(--period-count), minmax(17px, 1fr));

    align-items: start;
    justify-items: center;

    gap: 2px;

    min-width: 0;
}

.subject-row-year > :last-child,
.subject-row-period > :nth-last-child(-n + 2) {
    justify-self: center;
}
</style>
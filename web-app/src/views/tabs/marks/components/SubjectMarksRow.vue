<template>
    <div
        v-if="mode === 'period'"
        class="subject-row subject-row-period"
    >
        <button
            class="subject-name subject-name-button"
            type="button"
            @click="openSubjectRating"
        >
            {{ subject }}
        </button>

        <div class="subject-marks">
            <MarkBadge
                v-for="(mark, index) in marks"
                :key="index"
                :mark="mark"
                :interactive="Boolean(mark?.ratingKey)"
                :disabled="!mark?.ratingKey"
                @click="mark && emit('mark-rating', mark, subject)"
            />
        </div>

        <button
            class="subject-rating-button"
            type="button"
            @click="openSubjectRating"
        >
            <MarkBadge :mark="averageMark" />
        </button>

        <button
            class="subject-rating-button"
            type="button"
            @click="openSubjectRating"
        >
            <MarkBadge :mark="periodMark" />
        </button>
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
                :interactive="Boolean(mark?.ratingKey)"
                :disabled="!mark?.ratingKey"
                @click="mark && emit('mark-rating', mark, subject)"
            />

            <MarkBadge
                v-if="marks.length === 0"
                :mark="null"
            />
        </div>

        <MarkBadge
            :mark="finalMark"
            :interactive="Boolean(finalMark?.ratingKey)"
            :disabled="!finalMark?.ratingKey"
            @click="finalMark && emit('mark-rating', finalMark, subject)"
        />
    </div>
</template>

<script setup lang="ts">
import MarkBadge from "@/components/MarkBadge.vue";

import type { MarkLog } from "@/api/dnevnik";

const props = withDefaults(
    defineProps<{
        subject: string;
        mode: "period" | "year";
        marks: readonly (MarkLog | null)[];
        ratingKey?: string;
        averageMark?: MarkLog | null;
        periodMark?: MarkLog | null;
        finalMark?: MarkLog | null;
    }>(),
    {
        ratingKey: undefined,
        averageMark: null,
        periodMark: null,
        finalMark: null,
    },
);

const emit = defineEmits<{
    "mark-rating": [
        mark: MarkLog,
        subject: string,
    ];
    "subject-rating": [
        ratingKey: string,
        subject: string,
    ];
}>();

function openSubjectRating(): void {
    if (!props.ratingKey) {
        return;
    }

    emit(
        "subject-rating",
        props.ratingKey,
        props.subject,
    );
}
</script>

<style scoped>
.subject-row {
    display: grid;
    align-items: start;

    width: 100%;
    min-width: 0;

    padding: 5px 0;
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

.subject-name-button {
    padding: 0;

    border: 0;
    background: transparent;

    text-align: left;

    cursor: pointer;
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

.subject-rating-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    min-width: 0;
    padding: 0;

    border: 0;
    background: transparent;

    cursor: pointer;
}

.subject-row-year > :last-child,
.subject-row-period > :nth-last-child(-n + 2) {
    justify-self: center;
}
</style>
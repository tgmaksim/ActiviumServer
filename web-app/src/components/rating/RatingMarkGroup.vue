<template>
    <div
        v-if="marks.length"
        class="rating-group"
    >
        <span class="rating-group-title">
            {{ title }}
        </span>

        <div class="rating-marks">
            <MarkBadge
                v-for="(mark, index) in marks"
                :key="index"
                :mark="mark"
                size="rating"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import MarkBadge from "@/components/MarkBadge.vue";

import type { MarkLog } from "@/api/dnevnik";

defineProps<{
    title: string;
    marks: readonly MarkLog[];
}>();
</script>

<style scoped>
.rating-group {
    display: flex;
    flex: 1 1 auto;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;

    min-width: 0;
    padding: 4px 5px;
}

.rating-group-title {
    color: var(--text-primary);
    font-size: 15px;
    font-weight: 600;
}

.rating-marks {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 5px;

    margin-left: auto;
}
</style>
<template>
    <div
        v-if="visible"
        class="rating-stats"
    >
        <MarkBadge
            v-if="oldAvgMark"
            :mark="oldAvgMark"
            size="rating"
        />

        <RatingLoader
            v-else-if="loading"
        />

        <img
            class="rating-arrow"
            :src="arrowRight"
            alt=""
        />

        <MarkBadge
            v-if="newAvgMark"
            :mark="newAvgMark"
            size="rating"
        />

        <RatingLoader
            v-else-if="loading"
        />
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import MarkBadge from "@/components/MarkBadge.vue";

import RatingLoader from "./RatingLoader.vue";

import arrowRight from "@/assets/rating/arrow_right.svg";

import type { MarkLog } from "@/api/dnevnik";

const props = defineProps<{
    oldAvgMark: MarkLog | null;
    newAvgMark: MarkLog | null;
    loading: boolean;
}>();

const visible = computed(() =>
    props.loading ||
    props.oldAvgMark !== null ||
    props.newAvgMark !== null,
);
</script>

<style scoped>
.rating-stats {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    min-height: 42px;
    margin: 8px 0 12px;
}

.rating-arrow {
    flex: 0 0 auto;

    width: 20px;
    height: 20px;

    object-fit: contain;
}
</style>
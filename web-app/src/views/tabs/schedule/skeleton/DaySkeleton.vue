<template>
    <div class="day-skeleton">
        <LessonSkeleton
            v-for="item in lessonsCount"
            :key="item"
        />
    </div>
</template>

<script setup lang="ts">
import LessonSkeleton from "./LessonSkeleton.vue";

withDefaults(
    defineProps<{
        lessonsCount?: number;
    }>(),
    {
        lessonsCount: 5,
    },
);
</script>

<style scoped>
.day-skeleton {
    width: 100%;
    padding: 6px 5px 110px;
}
</style>
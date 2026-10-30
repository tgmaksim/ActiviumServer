<template>
    <div class="calendar-skeleton">
        <div
            v-for="item in count"
            :key="item"
            class="calendar-skeleton-day skeleton-shimmer"
        >
            <span class="calendar-skeleton-weekday"></span>
            <span class="calendar-skeleton-number"></span>
        </div>
    </div>
</template>

<script setup lang="ts">
withDefaults(
    defineProps<{
        count?: number;
    }>(),
    {
        count: 7,
    },
);
</script>

<style scoped>
.calendar-skeleton {
    display: flex;
    align-items: center;

    gap: 14px;

    width: 100%;
    padding: 0 5px;

    overflow: hidden;
}

.calendar-skeleton-day {
    display: flex;
    flex: 0 0 45px;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;

    width: 45px;
    height: 45px;

    padding: 9px 0;

    border: 1px solid var(--calendar-day-stroke);
    border-radius: 12px;
}

.calendar-skeleton-weekday {
    width: 18px;
    height: 4px;

    border-radius: 10px;
}

.calendar-skeleton-number {
    width: 22px;
    height: 14px;

    border-radius: 10px;
}

.skeleton-shimmer {
    background-image: linear-gradient(
        90deg,
        var(--skeleton-base) 0%,
        var(--skeleton-shimmer-center) 45%,
        var(--skeleton-highlight) 50%,
        var(--skeleton-shimmer-center) 55%,
        var(--skeleton-base) 100%
    );

    background-size: 200% 100%;

    animation: schedule-shimmer 1.5s ease-in-out infinite;
}

.skeleton-shimmer > span {
    background: var(--skeleton-base);
}

@keyframes schedule-shimmer {
    from {
        background-position: 100% 0;
    }

    to {
        background-position: -100% 0;
    }
}

@media (prefers-reduced-motion: reduce) {
    .skeleton-shimmer {
        animation: none;
    }
}
</style>
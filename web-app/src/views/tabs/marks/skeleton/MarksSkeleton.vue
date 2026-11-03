<template>
    <div
        v-if="mode === 'recent'"
        class="marks-recent-skeleton"
    >
        <div
            v-for="item in 7"
            :key="item"
            class="recent-skeleton-card"
        >
            <div class="recent-skeleton-value skeleton-shimmer"></div>
            <div class="recent-skeleton-subject skeleton-shimmer"></div>
            <div class="recent-skeleton-detail skeleton-shimmer"></div>
        </div>
    </div>

    <div
        v-else
        class="marks-table-skeleton"
    >
        <div
            v-for="item in 10"
            :key="item"
            class="marks-row-skeleton"
        >
            <div class="skeleton-subject skeleton-shimmer"></div>

            <div class="skeleton-marks">
                <span
                    v-for="mark in 3"
                    :key="mark"
                    class="skeleton-mark skeleton-shimmer"
                ></span>
            </div>

            <span class="skeleton-mark skeleton-shimmer"></span>
            <span class="skeleton-mark skeleton-shimmer"></span>
        </div>
    </div>
</template>

<script setup lang="ts">
defineProps<{
    mode: "recent" | "table";
}>();
</script>

<style scoped>
.marks-recent-skeleton {
    display: flex;
    gap: 0;

    padding: 8px;

    overflow: hidden;
}

.recent-skeleton-card {
    display: flex;
    flex: 0 0 90px;
    flex-direction: column;
    gap: 6px;

    padding: 4px;
}

.recent-skeleton-value {
    width: 100%;
    height: 40px;

    border-radius: 7px;
}

.recent-skeleton-subject {
    width: 75%;
    height: 8px;

    border-radius: 8px;
}

.recent-skeleton-detail {
    width: 55%;
    height: 7px;

    border-radius: 8px;
}

.marks-table-skeleton {
    display: flex;
    flex-direction: column;

    padding: 0 8px;
}

.marks-row-skeleton {
    display: grid;
    grid-template-columns:
        minmax(78px, 1fr)
        minmax(0, 2fr)
        23px
        23px;

    align-items: center;
    gap: 5px;

    min-height: 48px;

    margin-bottom: 7px;
    padding: 10px 8px;

    border: 1px solid var(--stroke-bg);
    border-radius: 12px;

    background: var(--lesson-bg);
}

.skeleton-subject {
    width: 80%;
    height: 9px;

    border-radius: 8px;
}

.skeleton-marks {
    display: flex;
    flex-wrap: wrap;
    gap: 3px;

    min-width: 0;
}

.skeleton-mark {
    display: block;

    width: 19px;
    height: 17px;

    border-radius: 5px;
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

    animation: marks-shimmer 1.5s ease-in-out infinite;
}

@keyframes marks-shimmer {
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
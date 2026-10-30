<template>
    <div class="lesson-skeleton">
        <div class="lesson-skeleton-content">
            <div class="lesson-skeleton-heading">
                <span class="skeleton-circle skeleton-shimmer"></span>
                <span class="skeleton-line skeleton-title skeleton-shimmer"></span>
            </div>

            <div class="lesson-skeleton-meta">
                <span class="skeleton-line skeleton-time skeleton-shimmer"></span>
                <span class="skeleton-line skeleton-place skeleton-shimmer"></span>
            </div>

            <div class="lesson-skeleton-homework">
                <span class="skeleton-circle skeleton-icon skeleton-shimmer"></span>
                <span class="skeleton-line skeleton-homework-text skeleton-shimmer"></span>
            </div>

            <span class="skeleton-line skeleton-note skeleton-shimmer"></span>

            <span class="skeleton-line skeleton-file skeleton-shimmer"></span>
        </div>

        <div class="lesson-skeleton-actions">
            <span class="skeleton-action skeleton-shimmer"></span>
            <span class="skeleton-action skeleton-shimmer"></span>
        </div>
    </div>
</template>

<style scoped>
.lesson-skeleton {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;

    gap: 12px;

    width: 100%;
    min-width: 0;

    margin-bottom: 8px;
    padding: 12px;

    border: 1px solid var(--stroke-bg);
    border-radius: 15px;

    background: var(--lesson-bg);
}

.lesson-skeleton-content {
    display: flex;
    flex: 1;
    flex-direction: column;

    min-width: 0;
}

.lesson-skeleton-heading,
.lesson-skeleton-meta,
.lesson-skeleton-homework {
    display: flex;
    align-items: center;
}

.lesson-skeleton-heading {
    gap: 10px;
}

.lesson-skeleton-meta {
    gap: 10px;
    margin-top: 10px;
}

.lesson-skeleton-homework {
    gap: 8px;
    margin-top: 10px;
}

.skeleton-circle {
    flex: 0 0 18px;

    width: 18px;
    height: 18px;

    border-radius: 50%;
}

.skeleton-icon {
    flex-basis: 12px;
    width: 12px;
    height: 12px;
}

.skeleton-line {
    display: block;

    height: 8px;

    border-radius: 10px;
}

.skeleton-title {
    width: 120px;
    height: 12px;
}

.skeleton-time {
    width: 70px;
}

.skeleton-place {
    width: 44px;
}

.skeleton-homework-text {
    width: min(180px, 75%);
}

.skeleton-note {
    width: min(220px, 85%);
    margin-top: 10px;
}

.skeleton-file {
    width: min(190px, 75%);
    margin-top: 10px;
}

.lesson-skeleton-actions {
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.skeleton-action {
    flex: 0 0 28px;

    width: 28px;
    height: 28px;

    border-radius: 8px;
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
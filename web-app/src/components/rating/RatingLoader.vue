<template>
    <span
        class="rating-loader"
        :class="`rating-loader-${size}`"
        role="status"
        aria-label="Загрузка"
    ></span>
</template>

<script setup lang="ts">
withDefaults(
    defineProps<{
        size?: "small" | "normal";
    }>(),
    {
        size: "normal",
    },
);
</script>

<style scoped>
.rating-loader {
    display: inline-block;
    flex: 0 0 auto;

    border: 2px solid var(--stroke-bg);
    border-top-color: var(--slider-accent);
    border-radius: 50%;

    animation: rating-loader 0.7s linear infinite;
}

.rating-loader-small {
    width: 16px;
    height: 16px;
}

.rating-loader-normal {
    width: 20px;
    height: 20px;
}

@keyframes rating-loader {
    to {
        transform: rotate(360deg);
    }
}
</style>
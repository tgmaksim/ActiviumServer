<template>
    <a
        class="ad-banner"
        :href="ad.url"
        target="_blank"
        rel="noopener noreferrer"
        @click="$emit('click', ad.adId)"
    >
        <div class="ad-image-container">
            <div
                v-if="!imageLoaded"
                class="ad-image-placeholder"
            ></div>

            <img
                v-if="ad.imageUrl"
                :src="ad.imageUrl"
                class="ad-image"
                :class="{ 'ad-image-loaded': imageLoaded }"
                alt=""
                loading="eager"
                decoding="async"
                @load="imageLoaded = true"
                @error="imageLoaded = false"
            />
        </div>

        <div class="ad-content">
            <div class="ad-title-container">
                <span class="ad-label">
                    Реклама
                </span>

                <span class="ad-title">
                    {{ ad.title }}
                </span>
            </div>

            <p class="ad-description">
                {{ ad.text }}
            </p>
        </div>
    </a>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

import type { Ad } from "@/api/ads";

const props = defineProps<{
    ad: Ad;
}>();

defineEmits<{
    click: [adId: number];
}>();

const imageLoaded = ref(false);

watch(
    () => props.ad.imageUrl,
    () => {
        imageLoaded.value = false;
    },
    { immediate: true },
);
</script>

<style scoped>
.ad-banner {
    display: flex;
    align-items: center;

    width: 100%;
    height: 80px;
    box-sizing: border-box;
    flex: 0 0 80px;

    padding: 5px;
    margin: 0 5px;
    margin-bottom: 5px;
    border: 1px solid var(--stroke-bg);
    border-radius: 15px;

    background: var(--lesson-bg);
    color: inherit;

    text-decoration: none;
    overflow: hidden;
    cursor: pointer;
}

.ad-image-container {
    position: relative;
    flex: 0 0 80px;

    width: 80px;
    height: 100%;

    overflow: hidden;
    border-radius: 12px;
    background: var(--skeleton-base);
}

.ad-image-placeholder {
    position: absolute;
    inset: 0;

    border-radius: 12px;
    background: var(--skeleton-base);
}

.ad-image {
    position: absolute;
    inset: 0;

    width: 100%;
    height: 100%;

    object-fit: contain;
    opacity: 0;

    transition: opacity 200ms ease;
}

.ad-image-loaded {
    opacity: 1;
}

.ad-content {
    display: flex;
    flex: 1;
    flex-direction: column;
    justify-content: center;

    min-width: 0;
    margin-left: 5px;
}

.ad-title-container {
    display: flex;
    align-items: center;

    width: 100%;
    min-width: 0;
}

.ad-label {
    flex-shrink: 0;

    padding: 2px 5px;
    border-radius: 5px;

    background: var(--ad-label-bg);
    color: var(--ad-label-text);

    font-size: 9px;
    line-height: normal;
}

.ad-title {
    flex: 1;
    min-width: 0;

    margin-left: 6px;

    color: var(--lesson-subject);

    font-size: 14px;
    font-weight: 700;

    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.ad-description {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;

    margin: 3px 0 0;

    color: var(--lesson-subject);
    opacity: 0.75;

    font-size: 11px;
    line-height: 1.3;

    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
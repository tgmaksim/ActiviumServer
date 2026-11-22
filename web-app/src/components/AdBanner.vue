<template>
    <a
        class="ad-banner"
        :class="{
            'ad-banner-birthday': ad.isDeveloperBirthday,
        }"
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
                <span
                    v-if="!ad.isDeveloperBirthday"
                    class="ad-label"
                >
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

        <!-- Праздничная анимация -->
        <div
            v-if="ad.isDeveloperBirthday"
            class="ad-balloons"
            aria-hidden="true"
        >
            <span class="ad-balloon ad-balloon-one">🎈</span>
            <span class="ad-balloon ad-balloon-two">🎈</span>
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
    position: relative;

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

.ad-title-container .ad-title:first-child {
    margin-left: 0;
}

.ad-description {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 4;

    margin: 3px 0 0;

    color: var(--lesson-subject);
    opacity: 0.75;

    font-size: 11px;
    line-height: 1.3;

    overflow: hidden;
    text-overflow: ellipsis;
}

/* Праздничная анимация */

.ad-balloons {
    position: absolute;
    inset: 0 0 0 auto;

    width: 38px;

    overflow: hidden;
    pointer-events: none;
}

.ad-balloon {
    position: absolute;
    top: 0;
    right: 5px;

    display: block;

    font-size: 17px;
    line-height: 1;

    opacity: 0;

    will-change: transform, opacity;

    animation: ad-balloon-float 4s linear infinite;
}

.ad-balloon-one {
    right: 5px;
    animation-duration: 4s;
}

.ad-balloon-two {
    right: 19px;

    font-size: 13px;

    animation-duration: 5s;
    animation-delay: -2s;
}

.ad-banner-birthday .ad-content {
    padding-right: 25px;
}

@keyframes ad-balloon-float {
    0% {
        transform: translateY(-22px) rotate(-12deg);
        opacity: 0;
    }

    12% {
        opacity: 1;
    }

    45% {
        transform: translateY(30px) rotate(10deg);
    }

    80% {
        opacity: 1;
    }

    100% {
        transform: translateY(100px) rotate(-10deg);
        opacity: 0;
    }
}

/* Небольшие экраны по высоте */

@media (max-height: 700px) {
    .ad-banner {
        height: 68px;
        flex-basis: 68px;
    }

    .ad-image-container {
        flex-basis: 56px;
        width: 56px;
    }

    .ad-image-placeholder {
        border-radius: 9px;
    }

    .ad-title {
        font-size: 12px;
        line-height: 1.1;
    }

    .ad-description {
        -webkit-line-clamp: 4;
        font-size: 9.5px;
        line-height: 1.1;
        margin-top: 2px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .ad-balloon {
        animation: none;
        opacity: 1;
    }
}
</style>
<template>
    <article
        ref="cardElement"
        class="school-post-card"
        role="button"
        tabindex="0"
        @click="onClick"
        @keydown.enter.prevent="onClick"
        @keydown.space.prevent="onClick"
    >
        <div class="school-post-title">
            {{ post.title }}
        </div>

        <div
            v-if="post.description"
            class="school-post-description"
        >
            {{ post.description }}
        </div>

        <div
            v-if="post.imageUrl"
            class="school-post-image-container"
        >
            <div
                v-if="!imageLoaded"
                class="school-post-image-placeholder"
            >
                <span>▧</span>
            </div>

            <img
                :src="post.imageUrl"
                class="school-post-image"
                :class="{
                    'school-post-image-loaded': imageLoaded,
                }"
                alt=""
                loading="lazy"
                decoding="async"
                @load="imageLoaded = true"
                @error="imageLoaded = false"
            />
        </div>

        <div class="school-post-author-row">
            <span class="school-post-author">
                {{ post.author }}
            </span>

            <span
                v-if="post.authorVerified"
                class="school-post-verified"
                aria-label="Проверенный автор"
            >
                ✓
            </span>

            <span class="school-post-date">
                {{ post.humanCreatedAt }}
            </span>

            <span
                v-if="post.isUpdated"
                class="school-post-updated"
            >
                {{ strings.schoolPostUpdated }}
            </span>
        </div>

        <div
            v-if="post.scheduleDate !== null"
            class="school-post-schedule"
        >
            {{ strings.schoolPostSchedule(post.humanScheduleDate ?? "") }}
        </div>

        <div class="school-post-footer">
            <span class="school-post-viewings">
                {{ strings.schoolPostViewings(post.countViewings) }}
            </span>

            <div class="school-post-likes">
                <span
                    class="school-post-like-icon"
                    :class="{
                        'school-post-like-active': post.hasMyLike,
                    }"
                >
                    {{ post.hasMyLike ? "♥" : "♡" }}
                </span>

                <span>{{ post.countLikes }}</span>
            </div>
        </div>
    </article>
</template>

<script setup lang="ts">
import {
    onBeforeUnmount,
    onMounted,
    ref,
    watch,
} from "vue";

import { strings } from "@/constants/strings";

import type { SchoolPost } from "@/api/school";

const props = withDefaults(
    defineProps<{
        post: SchoolPost;
        scrollRoot?: HTMLElement | null;
    }>(),
    {
        scrollRoot: null,
    },
);

const emit = defineEmits<{
    click: [postId: number];
    see: [postId: number];
}>();

const cardElement = ref<HTMLElement | null>(null);

const imageLoaded = ref(false);

let observer: IntersectionObserver | null = null;
let hasBeenSeen = false;

function onClick(): void {
    emit("click", props.post.postId);
}

/**
 * Карточка считается увиденной только после полной видимости.
 * Событие отправляется не более одного раза за её жизненный цикл.
 */
function onIntersection(
    entries: IntersectionObserverEntry[],
): void {
    const entry = entries[0];

    if (
        !entry ||
        !entry.isIntersecting ||
        entry.intersectionRatio < 1 ||
        hasBeenSeen ||
        props.post.isSaw
    ) {
        return;
    }

    hasBeenSeen = true;

    emit("see", props.post.postId);
}

function setupObserver(): void {
    observer?.disconnect();
    observer = null;

    const element = cardElement.value;

    if (!element) {
        return;
    }

    if ("IntersectionObserver" in window) {
        observer = new IntersectionObserver(
            onIntersection,
            {
                root: props.scrollRoot,
                threshold: 1,
            },
        );

        observer.observe(element);
    }
}

watch(
    () => props.scrollRoot,
    () => setupObserver(),
);

onMounted(setupObserver);

onBeforeUnmount(() => {
    observer?.disconnect();
    observer = null;
});
</script>

<style scoped>
.school-post-card {
    display: flex;
    flex-direction: column;

    width: 100%;
    min-width: 0;

    padding: 12px;
    margin-bottom: 8px;

    border: 1px solid var(--stroke-bg);
    border-radius: 15px;

    background: var(--lesson-bg);
    color: var(--text-primary);

    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
}

.school-post-card:active {
    opacity: 0.85;
}

.school-post-title {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.3;

    overflow-wrap: anywhere;
}

.school-post-description {
    margin-top: 4px;

    color: var(--text-secondary);

    font-size: 14px;
    line-height: 1.4;

    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.school-post-image-container {
    position: relative;

    width: 100%;
    height: 180px;

    margin-top: 10px;

    overflow: hidden;
    border-radius: 16px;

    background: var(--skeleton-base);
}

.school-post-image-placeholder {
    position: absolute;
    inset: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    color: var(--text-secondary);
    font-size: 32px;
}

.school-post-image {
    position: absolute;
    inset: 0;

    width: 100%;
    height: 100%;

    object-fit: cover;

    opacity: 0;
    transition: opacity 200ms ease;
}

.school-post-image-loaded {
    opacity: 1;
}

.school-post-author-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;

    min-width: 0;
    margin-top: 10px;

    font-size: 13px;
}

.school-post-author {
    color: var(--text-primary);
    font-weight: 700;
}

.school-post-verified {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    width: 15px;
    height: 15px;

    margin-left: 3px;

    border-radius: 50%;

    background: var(--slider-accent);
    color: #FFFFFF;

    font-size: 10px;
    font-weight: 700;
}

.school-post-date {
    margin-left: 8px;
    color: var(--text-secondary);
}

.school-post-updated {
    margin-left: 6px;
    color: var(--text-secondary);
}

.school-post-schedule {
    margin-top: 4px;

    color: var(--lesson-link);
    font-size: 13px;
}

.school-post-footer {
    display: flex;
    align-items: center;

    min-height: 18px;
    gap: 16px;

    margin-top: 8px;

    color: var(--text-secondary);
    font-size: 12px;
}

.school-post-likes {
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.school-post-like-icon {
    font-size: 16px;
    line-height: 1;
}

.school-post-like-active {
    color: #E53935;
}
</style>
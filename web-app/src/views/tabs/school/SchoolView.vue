<template>
    <div
        ref="scrollContainer"
        class="school-page"
        @scroll.passive="onScroll"
        @touchstart.passive="onTouchStart"
        @touchmove.passive="onTouchMove"
        @touchend="onTouchEnd"
        @touchcancel="onTouchEnd"
    >
        <AdBanner
            v-if="ad"
            :ad="ad"
            @click="(adId) => appViewModel?.clickAd(adId)"
        />

        <!-- Первоначальная загрузка -->
        <div
            v-if="isLoading"
            class="school-loading"
        >
            <span class="school-loader"></span>
        </div>

        <template v-else>
            <!-- Пустой список -->
            <div
                v-if="postsData?.posts.length === 0"
                class="school-no-posts"
            >
                {{ strings.noSchoolPosts }}
            </div>

            <!-- Список публикаций -->
            <div
                v-else
                ref="postsList"
                class="school-posts-list"
            >
                <SchoolPostCard
                    v-for="post in postsData?.posts ?? []"
                    :key="post.postId"
                    :post="post"
                    :scroll-root="scrollContainer"
                    @click="openPost"
                    @see="(postId) => schoolViewModel.seePost(postId)"
                />

                <!-- Загрузка следующей страницы -->
                <div
                    v-if="isRefreshing && postsData?.posts.length"
                    class="school-loading-more"
                >
                    <span class="school-loader"></span>
                </div>
            </div>
        </template>

        <!-- Обновление списка -->
        <span
            v-if="isRefreshing && !isLoading"
            class="school-refresh-loader"
            aria-label="Обновление публикаций"
        ></span>
    </div>

    <!-- Просмотр публикации -->
    <SchoolPostView
        v-if="selectedPost"
        :key="selectedPost.postId"
        :post="selectedPost"
        @close="closePost"
        @update-post="(result) => schoolViewModel.updatePostResult(result)"
    />
</template>

<script setup lang="ts">
import {
    computed,
    inject,
    nextTick,
    ref,
    watch,
} from "vue";

import { useRoute, useRouter } from "vue-router";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

import { useSettingsStore } from "@/stores/settings";

import {
    setShownCacheError,
} from "@/ui-core/state-utils";

import { CacheDataLoadState } from "@/ui-core/cache-data-load-state";

import { SchoolViewModel } from "./school-view-model";

import { appViewModelKey } from "@/views/app/app-view-model";

import SchoolPostCard from "@/components/SchoolPostCard.vue";
import AdBanner from "@/components/AdBanner.vue";
import SchoolPostView from "@/views/school-posts/SchoolPostView.vue";

import type { Ad } from "@/api/ads";

const settings = useSettingsStore();

const route = useRoute();
const router = useRouter();

const schoolViewModel = new SchoolViewModel();

const appViewModel = inject(appViewModelKey);

const ad = ref<Ad | null>(null);

const scrollContainer = ref<HTMLElement | null>(null);
const postsList = ref<HTMLElement | null>(null);

const postsData = computed(
    () => schoolViewModel.postsData.value,
);

const postsState = computed(
    () => schoolViewModel.postsState.value,
);

/**
 * Пока кэш не прочитан и данные не получены,
 * показываем первоначальную загрузку.
 */
const isLoading = computed(
    () => postsData.value === null,
);

/**
 * Состояние обновления списка.
 */
const isRefreshing = computed(
    () => postsState.value.type === "cloudLoading",
);

/**
 * Текущая публикация из query-параметра.
 */
const selectedPost = computed(() => {
    const value = route.query.schoolPostId;

    if (typeof value !== "string") {
        return null;
    }

    const postId = Number(value);

    if (!Number.isSafeInteger(postId)) {
        return null;
    }

    return postsData.value?.posts.find(
        post => post.postId === postId,
    ) ?? null;
});

/**
 * Состояния загрузки постов.
 *
 * Empty → CacheLoading → CacheSuccess → CloudLoading → CloudSuccess.
 */
watch(
    postsState,
    state => {
        switch (state.type) {
            case "empty":
                void schoolViewModel.loadCachePosts();
                break;

            case "cacheLoading":
                break;

            case "cacheSuccess":
                void schoolViewModel.loadCloudPosts();
                break;

            case "cacheError":
                Utilities.showUiMessage(state.message);
                void schoolViewModel.loadCloudPosts();
                break;

            case "cloudLoading":
                break;

            case "cloudSuccess":
                break;

            case "cloudError":
                Utilities.showUiMessage(state.message);

                setShownCacheError(
                    schoolViewModel.postsState,
                );
                break;

            case "shownError":
                break;
        }
    },
    {
        immediate: true,
    },
);

watch(
    () => schoolViewModel.postsWithoutVision.value,
    (count) => {
        if (count !== null) {
            appViewModel?.updateSchoolPostsCount(count);
        }
    },
);

/**
 * Рекламный баннер.
 */
if (appViewModel) {
    watch(
        () => appViewModel.adState.value,
        state => {
            ad.value = state.type === "success"
                ? state.data.ad
                : null;
        },
        {
            immediate: true,
        },
    );
}

/**
 * При смене профиля загружаем данные другого ребёнка.
 */
watch(
    () => settings.activeChildId,
    (childId, previousChildId) => {
        if (childId === previousChildId) {
            return;
        }

        schoolViewModel.resetPosts();

        // Закрываем публикацию, открытую для предыдущего профиля.
        void router.replace({
            path: route.path,
            query: {
                ...route.query,
                schoolPostId: undefined,
            },
        });
    },
);

/**
 * Обработка результатов нажатия на публикацию.
 */
watch(
    () => schoolViewModel.clickPostStates.value,
    states => {
        for (const [postId] of states) {
            schoolViewModel.resetClickPost(postId);
        }
    },
);

/**
 * Обработка результатов регистрации видимости публикации.
 */
watch(
    () => schoolViewModel.seePostStates.value,
    states => {
        for (const [postId] of states) {
            schoolViewModel.resetSeePost(postId);
        }
    },
);

/**
 * Открытие публикации.
 *
 * Создаём отдельную запись истории браузера.
 * Это позволяет закрывать публикацию системной кнопкой назад
 * и браузерным жестом без выхода со страницы Актив.
 */
async function openPost(postId: number): Promise<void> {
    const post = postsData.value?.posts.find(
        item => item.postId === postId,
    );

    if (!post || selectedPost.value?.postId === postId) {
        return;
    }

    await router.push({
        path: route.path,
        query: {
            ...route.query,
            schoolPostId: String(postId),
        },
        state: {
            schoolPostOverlay: true,
        },
    });

    // Регистрируем нажатие после открытия публикации.
    void schoolViewModel.clickPost(postId);
}

/**
 * Закрытие публикации.
 *
 * Если она была открыта внутри приложения,
 * возвращаемся на предыдущую запись истории.
 *
 * Если публикация открыта напрямую по ссылке,
 * просто удаляем query-параметр.
 */
function closePost(): void {
    if (window.history.state?.schoolPostOverlay === true) {
        router.back();
        return;
    }

    void router.replace({
        path: route.path,
        query: {
            ...route.query,
            schoolPostId: undefined,
        },
    });
}

/**
 * Проверка необходимости загрузки следующей страницы.
 *
 * Аналог порога в три карточки из Android.
 */
function checkPagination(): void {
    const container = scrollContainer.value;
    const list = postsList.value;
    const data = postsData.value;

    if (
        !container ||
        !list ||
        !data ||
        data.nextOffset === null
    ) {
        return;
    }

    const state = postsState.value;

    if (
        state.type !== "cloudSuccess" &&
        state.type !== "cloudError" &&
        state.type !== "shownError"
    ) {
        return;
    }

    const cards = Array.from(list.children);

    if (cards.length === 0) {
        return;
    }

    const containerBottom =
        container.getBoundingClientRect().bottom;

    let lastVisibleItem = -1;

    for (let i = 0; i < cards.length; i++) {
        const rect = cards[i].getBoundingClientRect();

        if (rect.top < containerBottom) {
            lastVisibleItem = i;
        }
    }

    const threshold = 3;

    if (lastVisibleItem >= cards.length - threshold) {
        void schoolViewModel.loadCloudPosts(
            data.nextOffset,
        );
    }
}

function onScroll(): void {
    checkPagination();
}

/**
 * После обновления списка проверяем пагинацию.
 *
 * Это также позволяет подгрузить следующую страницу,
 * если первая страница не заполнила область прокрутки.
 */
watch(
    postsData,
    async () => {
        await nextTick();
        checkPagination();
    },
);

/**
 * Pull-to-refresh.
 */
let touchStartY: number | null = null;
let pullDistance = 0;

function onTouchStart(event: TouchEvent): void {
    const container = scrollContainer.value;

    if (
        !container ||
        container.scrollTop > 0 ||
        isRefreshing.value
    ) {
        return;
    }

    touchStartY = event.touches[0]?.clientY ?? null;
    pullDistance = 0;
}

function onTouchMove(event: TouchEvent): void {
    if (touchStartY === null) {
        return;
    }

    const currentY = event.touches[0]?.clientY;

    if (currentY === undefined) {
        return;
    }

    pullDistance = currentY - touchStartY;

    if (pullDistance <= 0) {
        touchStartY = null;
        pullDistance = 0;
    }
}

function onTouchEnd(): void {
    const shouldRefresh = pullDistance >= 70;

    touchStartY = null;
    pullDistance = 0;

    if (shouldRefresh) {
        refreshPosts();
    }
}

function refreshPosts(): void {
    const state = postsState.value;

    if (
        state.type === "cloudSuccess" ||
        state.type === "cloudError" ||
        state.type === "shownError"
    ) {
        void schoolViewModel.loadCloudPosts();
    }
}
</script>

<style scoped>
.school-page {
    display: flex;
    flex-direction: column;

    position: relative;

    width: 100%;
    height: 100%;

    max-width: 720px;
    margin-inline: auto;

    min-width: 0;
    min-height: 0;

    padding: 5px 5px 100px;

    overflow-x: hidden;
    overflow-y: auto;

    overscroll-behavior-y: contain;
    touch-action: pan-y;

    scrollbar-width: none;
}

.school-page::-webkit-scrollbar {
    display: none;
}

.school-posts-list {
    width: 100%;
    min-width: 0;
}

.school-no-posts {
    width: 100%;

    padding: 5px;
    margin-top: 24px;

    border: 1px solid var(--stroke-bg);
    border-radius: 15px;

    background: var(--bg-login-about);
    color: var(--text-primary);

    font-size: 16px;
    font-style: italic;
    line-height: 1.5;

    text-align: center;
}

.school-loading {
    display: flex;
    align-items: center;
    justify-content: center;

    min-height: 150px;
}

.school-loading-more {
    display: flex;
    justify-content: center;

    padding: 15px;
}

.school-refresh-loader {
    position: absolute;
    top: 100px;
    right: 50%;

    display: inline-block;

    width: 30px;
    height: 30px;

    border: 5px solid var(--stroke-bg);
    border-top-color: var(--swipe-refresh-scheme);
    border-radius: 50%;

    animation: school-spin 0.7s linear infinite;

    transform: translateY(-50%);

    z-index: 10;
}

.school-loader {
    display: inline-block;

    width: 30px;
    height: 30px;

    border: 5px solid var(--stroke-bg);
    border-top-color: var(--swipe-refresh-scheme);
    border-radius: 50%;

    animation: school-spin 0.7s linear infinite;
}

@keyframes school-spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
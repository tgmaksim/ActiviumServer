<template>
    <div class="school-post-view">
        <iframe
            ref="postFrame"
            class="school-post-frame"
            :src="frameUrl"
            :title="post.title"
            allow="autoplay; fullscreen; picture-in-picture"
            allowfullscreen
            @load="onFrameLoad"
        ></iframe>

        <div
            v-if="frameLoading"
            class="school-post-frame-loading"
        >
            <span class="school-post-loader"></span>
        </div>

        <Transition name="school-post-toolbar">
            <div
                v-if="toolbarVisible"
                class="school-post-toolbar"
            >
                <button
                    class="school-post-toolbar-button"
                    type="button"
                    aria-label="Закрыть публикацию"
                    title="Закрыть"
                    @click="emit('close')"
                >
                    ×
                </button>

                <button
                    v-if="likeState.type !== 'shownError'"
                    class="school-post-toolbar-button school-post-like-button"
                    type="button"
                    :disabled="likeState.type === 'loading'"
                    :aria-label="post.hasMyLike ? 'Убрать реакцию' : 'Поставить реакцию'"
                    @click="toggleLike"
                >
                    <span
                        v-if="likeState.type === 'loading'"
                        class="school-post-like-loader"
                    ></span>

                    <span
                        v-else
                        :class="{
                            'school-post-like-active': post.hasMyLike,
                        }"
                    >
                        {{ post.hasMyLike ? "♥" : "♡" }}
                    </span>
                </button>

                <div
                    v-else
                    class="school-post-toolbar-button school-post-like-error"
                    title="Ошибка при отправке реакции"
                >
                    !
                </div>
            </div>
        </Transition>
    </div>
</template>

<script setup lang="ts">
import {
    computed,
    onBeforeUnmount,
    ref,
    watch,
} from "vue";

import { useSettingsStore } from "@/stores/settings";

import { Utilities } from "@/utils/utils";

import { SchoolPostViewModel } from "./school-post-view-model";

import type { SchoolPost, MarkSchoolPostResult } from "@/api/school";

const props = defineProps<{
    post: SchoolPost;
}>();

const emit = defineEmits<{
    close: [];
    updatePostResult: [result: MarkSchoolPostResult];
}>();

const settings = useSettingsStore();

const postFrame = ref<HTMLIFrameElement | null>(null);

const frameLoading = ref(true);
const toolbarVisible = ref(true);

const schoolPostViewModel = new SchoolPostViewModel(
    result => {
        emit("updatePostResult", result);
    },
);

const viewState = computed(
    () => schoolPostViewModel.viewState.value,
);

const likeState = computed(
    () => schoolPostViewModel.likeState.value,
);

const frameUrl = computed(() => {
    try {
        const url = new URL(
            props.post.postUrl,
            window.location.origin,
        );

        url.searchParams.set(
            "isDarkTheme",
            settings.darkTheme ? "true" : "false",
        );

        return url.toString();
    } catch {
        return props.post.postUrl;
    }
});

let viewSent = false;
let lastScrollY = 0;

let removeScrollTracking: (() => void) | null = null;

/**
 * Очистка обработчиков документа iframe.
 */
function clearScrollTracking(): void {
    removeScrollTracking?.();
    removeScrollTracking = null;
}

/**
 * Отправка полного просмотра.
 *
 * Android использует порог 100dp.
 * В браузере 100 CSS px соответствуют этому порогу.
 */
function sendViewed(): void {
    if (viewSent) {
        return;
    }

    viewSent = true;

    void schoolPostViewModel.viewPost(
        props.post.postId,
    );
}

/**
 * Обновление счётчиков внутри страницы поста.
 *
 * Работает при доступе к документу iframe с того же origin.
 */
function updateFrameCounter(
    method: "updateCountViewings" | "updateCountLikes",
    count: number,
): void {
    try {
        const frameWindow = postFrame.value?.contentWindow as
            | (Window & {
                updateCountViewings?: (value: number) => void;
                updateCountLikes?: (value: number) => void;
            })
            | null
            | undefined;

        frameWindow?.[method]?.(count);
    } catch {
        // Cross-origin iframe недоступен для прямого обращения.
    }
}

/**
 * Отслеживание прокрутки содержимого публикации.
 */
function setupScrollTracking(): void {
    clearScrollTracking();

    const frameWindow = postFrame.value?.contentWindow;
    const frameDocument = postFrame.value?.contentDocument;

    if (!frameWindow || !frameDocument) {
        return;
    }

    try {
        lastScrollY = frameWindow.scrollY;

        function onScroll(): void {
            const root = frameDocument.documentElement;
            const body = frameDocument.body;

            const contentHeight = Math.max(
                root.scrollHeight,
                body?.scrollHeight ?? 0,
            );

            const scrollY = Math.max(
                frameWindow.scrollY,
                root.scrollTop,
                body?.scrollTop ?? 0,
            );

            const viewportHeight = frameWindow.innerHeight;

            // Отправка полного просмотра.
            const remaining =
                contentHeight - scrollY - viewportHeight;

            if (remaining <= 100) {
                sendViewed();
            }

            // Управление видимостью нижней панели.
            const difference = scrollY - lastScrollY;

            if (Math.abs(difference) > 15) {
                toolbarVisible.value = difference < 0;
                lastScrollY = scrollY;
            }
        }

        frameWindow.addEventListener(
            "scroll",
            onScroll,
            { passive: true },
        );

        frameWindow.addEventListener(
            "resize",
            onScroll,
        );

        removeScrollTracking = () => {
            frameWindow.removeEventListener(
                "scroll",
                onScroll,
            );

            frameWindow.removeEventListener(
                "resize",
                onScroll,
            );
        };

        // Проверка короткой публикации сразу после загрузки.
        onScroll();
    } catch {
        // Браузер запрещает доступ к cross-origin документу.
        clearScrollTracking();
    }
}

function onFrameLoad(): void {
    frameLoading.value = false;

    setupScrollTracking();
}

/**
 * Изменение реакции.
 */
function toggleLike(): void {
    if (
        likeState.value.type === "loading" ||
        likeState.value.type === "shownError"
    ) {
        return;
    }

    void schoolPostViewModel.likePost(
        props.post.postId,
        !props.post.hasMyLike,
    );
}

/**
 * Результат регистрации полного просмотра.
 */
watch(viewState, state => {
    switch (state.type) {
        case "success":
            updateFrameCounter(
                "updateCountViewings",
                state.data.post.countViewings,
            );

            schoolPostViewModel.resetView();
            break;

        case "error":
            Utilities.showUiMessage(state.message);
            schoolPostViewModel.resetView();
            break;
    }
});

/**
 * Результат изменения реакции.
 */
watch(likeState, state => {
    switch (state.type) {
        case "success":
            updateFrameCounter(
                "updateCountLikes",
                state.data.post.countLikes,
            );

            schoolPostViewModel.resetLike();
            break;

        case "error":
            Utilities.showUiMessage(state.message);
            schoolPostViewModel.resetLikeError();
            break;
    }
});

/**
 * При смене публикации сбрасываем состояния и отслеживание.
 */
watch(
    () => props.post.postId,
    () => {
        clearScrollTracking();

        viewSent = false;
        lastScrollY = 0;

        frameLoading.value = true;
        toolbarVisible.value = true;

        schoolPostViewModel.reset();
    },
);

onBeforeUnmount(() => {
    clearScrollTracking();

    schoolPostViewModel.reset();
});
</script>

<style scoped>
.school-post-view {
    position: fixed;
    inset: 0;
    z-index: 2000;

    width: 100%;
    height: 100%;
    height: 100dvh;

    overflow: hidden;

    background: var(--main-bg);
}

.school-post-frame {
    display: block;

    width: 100%;
    height: 100%;

    border: 0;

    background: var(--main-bg);
}

.school-post-frame-loading {
    position: absolute;
    inset: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    background: var(--main-bg);
}

.school-post-loader,
.school-post-like-loader {
    display: block;

    width: 30px;
    height: 30px;

    border: 4px solid var(--stroke-bg);
    border-top-color: var(--swipe-refresh-scheme);
    border-radius: 50%;

    animation: school-post-spin 0.7s linear infinite;
}

.school-post-toolbar {
    position: absolute;

    right: 20px;
    bottom: calc(20px + env(safe-area-inset-bottom));
    left: 20px;

    display: flex;
    align-items: center;
    justify-content: space-around;

    height: 56px;

    border: 1px solid var(--stroke-bg);
    border-radius: 32px;

    background: var(--bg-bottom-menu);

    transition: opacity 180ms ease;
}

.school-post-toolbar-button {
    display: flex;
    align-items: center;
    justify-content: center;

    width: 40px;
    height: 40px;

    padding: 0;

    border: 0;
    border-radius: 12px;

    background: var(--button-bg);
    color: var(--text-primary);

    font-size: 27px;
    line-height: 1;

    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
}

.school-post-toolbar-button:disabled {
    opacity: 0.6;
    cursor: default;
}

.school-post-like-button {
    font-size: 25px;
}

.school-post-like-active {
    color: #E53935;
}

.school-post-like-loader {
    width: 22px;
    height: 22px;

    border-width: 3px;
}

.school-post-like-error {
    color: #E53935;
    font-size: 20px;
    font-weight: 700;
}

.school-post-toolbar-enter-active,
.school-post-toolbar-leave-active {
    transition:
        opacity 180ms ease,
        transform 180ms ease;
}

.school-post-toolbar-enter-from,
.school-post-toolbar-leave-to {
    opacity: 0;
    transform: translateY(12px);
}

@keyframes school-post-spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
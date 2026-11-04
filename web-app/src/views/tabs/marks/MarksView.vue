<template>
    <div
        ref="scrollContainer"
        class="marks-page"
        @touchstart.passive="onTouchStart"
        @touchmove.passive="onTouchMove"
        @touchend="onTouchEnd"
        @touchcancel="onTouchEnd"
    >
        <AdBanner
            v-if="ad"
            :ad="ad"
            @click="(adId) => appViewModel.clickAd(adId)"
        />

        <span
            v-if="isRefreshing"
            class="marks-refresh-loader"
            aria-label="Загрузка оценок"
        ></span>

        <!-- Последние оценки -->
        <div class="marks-recent-container">
            <div
                v-if="isLoading"
                class="marks-recent-list"
            >
                <MarksSkeleton mode="recent" />
            </div>

            <div
                v-else
                class="marks-recent-list"
            >
                <LastMarkCard
                    v-for="(mark, index) in marksData?.recentMarks ?? []"
                    :key="mark.ratingKey || index"
                    :mark="mark"
                    @rating="openRecentMarkRating"
                />
            </div>
        </div>

        <!-- Рейтинг в классе -->
        <button
            class="marks-rating-button"
            type="button"
            @click="onClassRatingClick"
        >
            {{ strings.classRating }}
        </button>

        <!-- Переключение таблиц -->
        <div
            class="marks-switch"
            role="tablist"
            aria-label="Период оценок"
        >
            <button
                class="marks-switch-item"
                :class="{
                    'marks-switch-item-selected': currentTable === 'period',
                }"
                type="button"
                role="tab"
                :aria-selected="currentTable === 'period'"
                @click="selectTable('period')"
            >
                {{ strings.marksCurrent }}
            </button>

            <button
                class="marks-switch-item"
                :class="{
                    'marks-switch-item-selected': currentTable === 'year',
                }"
                type="button"
                role="tab"
                :aria-selected="currentTable === 'year'"
                @click="selectTable('year')"
            >
                {{ strings.marksYear }}
            </button>
        </div>

        <!-- Таблица оценок -->
        <div class="marks-table-container">
            <MarksSkeleton
                v-if="isLoading"
                mode="table"
            />

            <template v-else-if="currentTable === 'period'">
                <SubjectMarksRow
                    v-for="subject in visiblePeriodMarks"
                    :key="subject.ratingKey"
                    :subject="subject.subject"
                    :rating-key="subject.ratingKey"
                    mode="period"
                    :marks="subject.marks"
                    :average-mark="subject.averageMark"
                    :period-mark="subject.periodMark"
                    @mark-rating="openMarkRating"
                    @subject-rating="openSubjectRating"
                />
            </template>

            <template v-else>
                <SubjectMarksRow
                    v-for="(subject, index) in visibleYearMarks"
                    :key="`${subject.subject}-${index}`"
                    :subject="subject.subject"
                    mode="year"
                    :marks="subject.marks"
                    :final-mark="subject.finalMark"
                    @mark-rating="openMarkRating"
                />
            </template>
        </div>
    </div>

    <MarkRatingSheet
        v-if="selectedMarkRating"
        v-model="showMarkRating"
        :rating-key="selectedMarkRating.ratingKey"
        :subject="selectedMarkRating.subject"
        :mark="selectedMarkRating.mark"
    />

    <SubjectRatingSheet
        v-if="selectedSubjectRating"
        v-model="showSubjectRating"
        :rating-key="selectedSubjectRating.ratingKey"
        :subject="selectedSubjectRating.subject"
        :class-rating="selectedSubjectRating.classRating"
    />
</template>

<script setup lang="ts">
import {
    inject,
    computed,
    ref,
    watch,
} from "vue";

import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

import { useSettingsStore } from "@/stores/settings";

import {
    setShownError,
} from "@/ui-core/state-utils";

import { CacheDataLoadState } from "@/ui-core/cache-data-load-state";

import { MarksViewModel } from "./marks-view-model";
import { appViewModelKey } from "@/views/app/app-view-model";

import LastMarkCard from "./components/LastMarkCard.vue";
import SubjectMarksRow from "./components/SubjectMarksRow.vue";
import MarksSkeleton from "./skeleton/MarksSkeleton.vue";
import MarkRatingSheet from "@/components/rating/MarkRatingSheet.vue";
import SubjectRatingSheet from "./rating/SubjectRatingSheet.vue";
import AdBanner from "@/components/AdBanner.vue";

import type {
    MarkLog,
    MarkLast,
    MarksSubjectPeriod,
    MarksSubjectFinal,
} from "@/api/dnevnik";
import type { Ad } from "@/api/ads";

interface SelectedMarkRating {
    ratingKey: string;
    subject: string;
    mark: MarkLog;
}

interface SelectedSubjectRating {
    ratingKey: string;
    subject: string | null;
    classRating: boolean;
}

const settings = useSettingsStore();

const marksViewModel = new MarksViewModel();
const appViewModel = inject(appViewModelKey);

const ad = ref<Ad | null>(null);

const marksData = computed(
    () => marksViewModel.marksData.value,
);

const marksState = computed(
    () => marksViewModel.marksState.value,
);

const finalMarksState = computed(
    () => marksViewModel.finalMarksState.value,
);

/**
 * Пока кэш не прочитан и данные не получены,
 * показываем skeleton-компоненты.
 */
const isLoading = computed(
    () => marksData.value === null,
);

/**
 * Общая индикация обновления основных и годовых оценок.
 */
const isRefreshing = computed(() =>
    marksState.value.type === "cloudLoading" ||
    finalMarksState.value.type === "cloudLoading",
);

type MarksTable = "period" | "year";

const currentTable = ref<MarksTable>("period");

const showMarkRating = ref(false);
const selectedMarkRating = ref<SelectedMarkRating | null>(null);

const showSubjectRating = ref(false);
const selectedSubjectRating = ref<SelectedSubjectRating | null>(null);

/**
 * Предметы фильтруются непосредственно по настройке.
 * При её изменении таблица обновляется автоматически.
 */
const visiblePeriodMarks = computed(() => {
    const marks = marksData.value?.periodMarks ?? [];

    return filterPeriodMarks(
        marks,
        settings.showNullSubjectMarks,
    );
});

const visibleYearMarks = computed(() => {
    const marks = marksData.value?.finalMarks ?? [];

    return filterYearMarks(
        marks,
        settings.showNullSubjectMarks,
    );
});

function filterPeriodMarks(
    marks: MarksSubjectPeriod[],
    showNull: boolean,
): MarksSubjectPeriod[] {
    if (showNull) {
        return marks;
    }

    return marks.filter(subject =>
        subject.marks.length > 0 ||
        subject.averageMark !== null ||
        subject.periodMark !== null,
    );
}

function filterYearMarks(
    marks: MarksSubjectFinal[],
    showNull: boolean,
): MarksSubjectFinal[] {
    if (showNull) {
        return marks;
    }

    return marks.filter(subject =>
        subject.marks.some(mark => mark !== null) ||
        subject.finalMark !== null,
    );
}

if (appViewModel) {
    watch(
        () => appViewModel.adState.value,
        (state) => {
            ad.value = state.type === "success"
                ? state.data.ad
                : null;
        },
        { immediate: true },
    );
}

/**
 * Общий обработчик состояний основных оценок.
 *
 * Empty → CacheLoading → CacheSuccess → CloudLoading → CloudSuccess.
 */
watch(
    marksState,
    (state) => {
        switch (state.type) {
            case "empty":
                void marksViewModel.loadCacheMarks();
                break;

            case "cacheLoading":
                break;

            case "cacheSuccess":
                marksViewModel.loadCloudMarks();
                break;

            case "cacheError":
                Utilities.showUiMessage(state.message);
                marksViewModel.loadCloudMarks();
                break;

            case "cloudLoading":
                break;

            case "cloudSuccess":
                break;

            case "cloudError":
                Utilities.showUiMessage(state.message);
                setShownError(marksViewModel.marksState);
                break;

            case "shownError":
                break;
        }
    },
    {
        immediate: true,
    },
);

/**
 * Годовые оценки загружаются отдельно и только при необходимости.
 */
watch(
    finalMarksState,
    (state) => {
        switch (state.type) {
            case "empty":
                break;

            case "cacheLoading":
                break;

            case "cacheSuccess":
                marksViewModel.loadCloudFinalMarks();
                break;

            case "cacheError":
                Utilities.showUiMessage(state.message);
                marksViewModel.loadCloudFinalMarks();
                break;

            case "cloudLoading":
                break;

            case "cloudSuccess":
                break;

            case "cloudError":
                Utilities.showUiMessage(state.message);
                setShownError(marksViewModel.finalMarksState);
                break;

            case "shownError":
                break;
        }
    },
);

/**
 * Изменение периода последних оценок.
 * Повторно загружаем основные оценки, не очищая отображаемые данные.
 */
watch(
    () => settings.lastMarksPeriod,
    (period, previousPeriod) => {
        if (period === previousPeriod) {
            return;
        }

        marksViewModel.loadCloudMarks();
    },
);

/**
 * Смена ребёнка полностью перезапускает загрузку.
 */
watch(
    () => settings.activeChildId,
    (childId, previousChildId) => {
        if (childId === previousChildId) {
            return;
        }

        currentTable.value = "period";

        showMarkRating.value = false;
        selectedMarkRating.value = null;

        showSubjectRating.value = false;
        selectedSubjectRating.value = null;

        marksViewModel.resetMarks();
    },
);

/**
 * Переключение текущей таблицы.
 */
function selectTable(table: MarksTable): void {
    if (currentTable.value === table) {
        return;
    }

    currentTable.value = table;

    if (
        table === "year" &&
        marksData.value?.finalMarks.length === 0 &&
        finalMarksState.value.type === "empty"
    ) {
        void marksViewModel.loadCacheFinalMarks();
    }
}

/**
 * Рейтинг последней оценки.
 */
function openRecentMarkRating(mark: MarkLast): void {
    selectedMarkRating.value = {
        ratingKey: mark.ratingKey,
        subject: mark.subject,
        mark: mark.mark,
    };

    showMarkRating.value = true;

    marksViewModel.doneStudyMarkRating();
}

/**
 * Рейтинг оценки из таблицы.
 */
function openMarkRating(
    mark: MarkLog,
    subject: string,
): void {
    if (!mark.ratingKey) {
        return;
    }

    selectedMarkRating.value = {
        ratingKey: mark.ratingKey,
        subject,
        mark,
    };

    showMarkRating.value = true;

    marksViewModel.doneStudyMarkRating();
}

/**
 * Рейтинг конкретного предмета.
 */
function openSubjectRating(
    ratingKey: string,
    subject: string,
): void {
    selectedSubjectRating.value = {
        ratingKey,
        subject,
        classRating: false,
    };

    showSubjectRating.value = true;

    marksViewModel.doneStudySubjectRating();
}

/**
 * Общий рейтинг класса.
 */
function onClassRatingClick(): void {
    const ratingKey = marksData.value?.ratingKey;

    if (!ratingKey) {
        return;
    }

    selectedSubjectRating.value = {
        ratingKey,
        subject: null,
        classRating: true,
    };

    showSubjectRating.value = true;
}

/**
 * Pull-to-refresh.
 *
 * Обновление доступно после завершения первоначальной загрузки.
 */
const scrollContainer = ref<HTMLElement | null>(null);

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
        refreshMarks();
    }
}

function refreshMarks(): void {
    const state = marksState.value;

    if (
        state.type === "cloudSuccess" ||
        state.type === "cloudError" ||
        state.type === "shownError"
    ) {
        marksViewModel.loadCloudMarks();
    }
}
</script>

<style scoped>
.marks-page {
    display: flex;
    flex-direction: column;
    position: relative;

    width: 100%;
    height: 100%;

    max-width: 720px;
    margin-inline: auto;

    min-width: 0;
    min-height: 0;

    padding: 5px 0 100px;

    overflow-x: hidden;
    overflow-y: auto;

    overscroll-behavior-y: contain;
    touch-action: pan-y;

    scrollbar-width: none;
}

.marks-page::-webkit-scrollbar {
    display: none;
}

.marks-recent-container {
    width: 100%;
    min-width: 0;
}

.marks-recent-list {
    display: flex;

    width: 100%;
    min-width: 0;

    overflow-x: auto;
    overflow-y: hidden;

    scrollbar-width: none;
    overscroll-behavior-x: contain;
}

.marks-recent-list::-webkit-scrollbar {
    display: none;
}

.marks-rating-button {
    flex: 0 0 40px;

    height: 40px;

    margin: 10px 18px;

    border: 1px solid var(--stroke-bg);
    border-radius: 12px;

    background: var(--button-bg);
    color: var(--text-primary);

    font-size: 14px;
    font-weight: bold;
    text-transform: uppercase;

    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
}

.marks-rating-button:active {
    opacity: 0.75;
}

.marks-switch {
    display: flex;
    flex: 0 0 30px;

    height: 30px;

    gap: 2px;

    margin: 6px 18px 10px;
    padding: 2px;

    border: 1px solid var(--stroke-bg);
    border-radius: 14px;

    background: var(--bg-marks-switch-block);
}

.marks-switch-item {
    flex: 1;
    min-width: 0;

    border: 0;
    border-radius: 12px;

    background: transparent;
    color: var(--text-primary);

    font-size: 12px;
    font-weight: bold;

    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
}

.marks-switch-item-selected {
    background: var(--bg-marks-switch);
}

.marks-table-container {
    width: 100%;
    min-width: 0;

    padding: 0 8px;
}

.marks-refresh-loader {
    position: absolute;
    top: 100px;
    right: 50%;

    display: inline-block;

    width: 30px;
    height: 30px;

    border: 5px solid var(--stroke-bg);
    border-top-color: var(--slider-accent);
    border-radius: 50%;

    animation: marks-loader 0.7s linear infinite;

    transform: translateY(-50%);

    z-index: 1000;
}

@keyframes marks-loader {
    to {
        transform: translateY(-50%) rotate(360deg);
    }
}
</style>
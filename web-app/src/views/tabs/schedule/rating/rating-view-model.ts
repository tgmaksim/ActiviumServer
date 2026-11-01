import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel, { CacheNullException } from "@/ui-core/ui-view-model";
import { CacheDataLoadState } from "@/ui-core/cache-data-load-state";

import { Dnevnik } from "@/api/dnevnik";
import type { LessonRatingStatsResult } from "@/api/dnevnik";

import { CacheManager } from "@/data/cache/cache-manager";
import { useSettingsStore } from "@/stores/settings";
import { Utilities } from "@/utils/utils";

import type { StringResourceKey } from "@/constants/strings";

export class RatingViewModel extends UiViewModel {
    private readonly settingsStore = useSettingsStore();

    private cacheRatingRequestId = 0;
    private isLoadingCacheRating = false;

    readonly lessonRatingState: Ref<CacheDataLoadState> = ref(
        CacheDataLoadState.empty(),
    );

    readonly lessonRatingData: Ref<LessonRatingStatsResult | null> = ref(null);

    static readonly CACHE_LESSON_RATING_STATS_NAME = "lesson_rating_stats";

    resetLessonRating(): void {
        this.cacheRatingRequestId++;
        this.isLoadingCacheRating = false;

        this.lessonRatingData.value = null;
        this.lessonRatingState.value = CacheDataLoadState.empty();
    }

    async loadCacheLessonRatingStats(ratingKey: string): Promise<void> {
        if (this.isLoadingCacheRating) {
            return;
        }

        this.isLoadingCacheRating = true;

        const requestId = ++this.cacheRatingRequestId;

        this.lessonRatingState.value = CacheDataLoadState.cacheLoading();

        const childId = this.settingsStore.activeChildId;

        try {
            try {
                const entity = await CacheManager.read(
                    childId,
                    RatingViewModel.CACHE_LESSON_RATING_STATS_NAME,
                    ratingKey,
                );

                if (!entity) {
                    throw new CacheNullException();
                }

                const lessonRatingStats = JSON.parse(
                    entity.value,
                ) as LessonRatingStatsResult;

                if (requestId !== this.cacheRatingRequestId) {
                    return;
                }

                this.lessonRatingData.value = lessonRatingStats;
                this.lessonRatingState.value = CacheDataLoadState.cacheSuccess();
            } catch (error: unknown) {
                if (requestId !== this.cacheRatingRequestId) {
                    return;
                }

                if (!(error instanceof CacheNullException)) {
                    Utilities.log(
                        error instanceof Error
                            ? error
                            : new Error(String(error)),
                        "Error at loadCacheLessonRatingStats",
                    );

                    await CacheManager.writeDnevnikCache(
                        childId,
                        RatingViewModel.CACHE_LESSON_RATING_STATS_NAME,
                        "",
                        ratingKey,
                    );

                    if (requestId !== this.cacheRatingRequestId) {
                        return;
                    }
                }

                this.lessonRatingState.value = CacheDataLoadState.cacheSuccess();
            }
        } finally {
            if (requestId === this.cacheRatingRequestId) {
                this.isLoadingCacheRating = false;
            }
        }
    }

    loadCloudLessonRatingStats(ratingKey: string): void {
        const childId = this.settingsStore.activeChildId;

        void this.executeRequest(
            this.lessonRatingState,
            this.lessonRatingData,
            "lessonRatingStats",
            "errorLessonRatingStats" as StringResourceKey,
            () => Dnevnik.getLessonRatingStats(ratingKey),
            (response) => response.answer,
            async (response) => {
                const answer = response.answer;

                if (!answer) {
                    return;
                }

                await CacheManager.writeDnevnikCache(
                    childId,
                    RatingViewModel.CACHE_LESSON_RATING_STATS_NAME,
                    JSON.stringify(answer),
                    ratingKey,
                );
            },
            {
                key: "lessonRatingStats",
                cancelPrevious: true,
            },
        );
    }
}
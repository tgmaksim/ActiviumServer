import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel, {
    CacheNullException,
} from "@/ui-core/ui-view-model";

import { CacheDataLoadState } from "@/ui-core/cache-data-load-state";
import { LoadState } from "@/ui-core/load-state";

import { Dnevnik } from "@/api/dnevnik";
import { Praise } from "@/api/praise";

import type {
    LessonRatingStatsResult,
    MarksRatingStatsResult,
    MarksSubjectRatingResult,
} from "@/api/dnevnik";

import { CacheManager } from "@/data/cache/cache-manager";
import { useSettingsStore } from "@/stores/settings";

import { Utilities } from "@/utils/utils";

import type { StringResourceKey } from "@/constants/strings";

type RatingApiResponse<T> = {
    status: boolean;
    answer: T | null;
    error?: {
        type?: string | null;
        errorMessage?: string | null;
    } | null;
};

interface RatingViewModelConfig<T> {
    cacheName: string;
    requestKey: string;
    apiName: string;
    errorKey: StringResourceKey;

    request: (
        ratingKey: string,
    ) => Promise<RatingApiResponse<T>>;

    transformCache?: (data: T) => T;
}

/**
 * Общая бизнес-логика загрузки рейтингов.
 *
 * Последовательность:
 * Empty → CacheLoading → CacheSuccess → CloudLoading → CloudSuccess.
 */
export class RatingDataViewModel<T> extends UiViewModel {
    private readonly settingsStore = useSettingsStore();

    private cacheRequestId = 0;
    private isLoadingCache = false;

    readonly state: Ref<CacheDataLoadState> = ref(
        CacheDataLoadState.empty(),
    );

    readonly data: Ref<T | null> = ref(null);

    constructor(
        private readonly config: RatingViewModelConfig<T>,
    ) {
        super();
    }

    reset(): void {
        this.cacheRequestId++;
        this.isLoadingCache = false;

        this.cancelRequest(this.config.requestKey);

        this.state.value = CacheDataLoadState.empty();
        this.data.value = null;
    }

    resetError(): void {
        this.state.value = CacheDataLoadState.shownError();
    }

    async loadCache(ratingKey: string): Promise<void> {
        if (this.isLoadingCache) {
            return;
        }

        this.isLoadingCache = true;

        const requestId = ++this.cacheRequestId;
        const childId = this.settingsStore.activeChildId;

        this.state.value = CacheDataLoadState.cacheLoading();

        try {
            const entity = await CacheManager.read(
                childId,
                this.config.cacheName,
                ratingKey,
            );

            if (requestId !== this.cacheRequestId) {
                return;
            }

            if (!entity) {
                throw new CacheNullException();
            }

            const cachedData = JSON.parse(entity.value) as T;

            this.data.value = this.config.transformCache
                ? this.config.transformCache(cachedData)
                : cachedData;

            this.state.value = CacheDataLoadState.cacheSuccess();
        } catch (error: unknown) {
            if (requestId !== this.cacheRequestId) {
                return;
            }

            if (!(error instanceof CacheNullException)) {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    `Error at loadCache ${this.config.apiName}`,
                );

                try {
                    await CacheManager.writeDnevnikCache(
                        childId,
                        this.config.cacheName,
                        "",
                        ratingKey,
                    );
                } catch (cacheError: unknown) {
                    Utilities.log(
                        cacheError instanceof Error
                            ? cacheError
                            : new Error(String(cacheError)),
                        `Error at clear cache ${this.config.apiName}`,
                    );
                }

                if (requestId !== this.cacheRequestId) {
                    return;
                }
            }

            this.state.value = CacheDataLoadState.cacheSuccess();
        } finally {
            if (requestId === this.cacheRequestId) {
                this.isLoadingCache = false;
            }
        }
    }

    loadCloud(ratingKey: string): void {
        const childId = this.settingsStore.activeChildId;

        void this.executeRequest(
            this.state,
            this.data,
            this.config.apiName,
            this.config.errorKey,
            () => this.config.request(ratingKey),
            response => response.answer,
            async response => {
                const answer = response.answer;

                if (!answer) {
                    return;
                }

                await CacheManager.writeDnevnikCache(
                    childId,
                    this.config.cacheName,
                    JSON.stringify(answer),
                    ratingKey,
                );
            },
            {
                key: this.config.requestKey,
                cancelPrevious: true,
            },
        );
    }
}

/**
 * Статистика оценок конкретного урока в расписании.
 */
export class LessonRatingViewModel
    extends RatingDataViewModel<LessonRatingStatsResult> {
    static readonly CACHE_NAME = "lesson_rating_stats";

    constructor() {
        super({
            cacheName: LessonRatingViewModel.CACHE_NAME,
            requestKey: "lessonRatingStats",
            apiName: "lessonRatingStats",
            errorKey: "errorLessonRatingStats",

            request: ratingKey =>
                Dnevnik.getLessonRatingStats(ratingKey),
        });
    }
}

/**
 * Рейтинг конкретной оценки.
 */
export class MarkRatingViewModel
    extends RatingDataViewModel<MarksRatingStatsResult> {
    static readonly CACHE_NAME = "marks_rating_stats";

    readonly praiseState = ref<LoadState<Record<string, never>>>(
        LoadState.empty(),
    );

    constructor() {
        super({
            cacheName: MarkRatingViewModel.CACHE_NAME,
            requestKey: "markRatingStats",
            apiName: "markRatingStats",
            errorKey: "errorMarks",

            request: ratingKey =>
                Dnevnik.getMarksRatingStats(ratingKey),

            // Как и в Android, право на похвалу
            // не берём из кэша: оно проверяется сервером.
            transformCache: data => ({
                ...data,
                hasAbilityPraise: false,
            }),
        });
    }

    sendPraise(
        ratingKey: string,
        text: string | null,
    ): void {
        void this.executeRequest(
            this.praiseState,
            "praise",
            "errorPraise",
            () => Praise.sendForMark(ratingKey, text),
            () => ({}),
        );
    }

    resetPraise(): void {
        this.praiseState.value = LoadState.empty();
    }

    resetPraiseError(): void {
        this.praiseState.value = LoadState.shownError();
    }
}

/**
 * Рейтинг по предмету или общий рейтинг класса.
 */
export class SubjectRatingViewModel
    extends RatingDataViewModel<MarksSubjectRatingResult> {
    static readonly CACHE_NAME = "subject_rating";

    constructor() {
        super({
            cacheName: SubjectRatingViewModel.CACHE_NAME,
            requestKey: "subjectRating",
            apiName: "subjectRating",
            errorKey: "errorMarks",

            request: ratingKey =>
                Dnevnik.getMarksSubjectRating(ratingKey),
        });
    }
}
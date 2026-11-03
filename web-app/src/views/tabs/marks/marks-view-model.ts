import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel, { CacheNullException } from "@/ui-core/ui-view-model";
import { CacheDataLoadState } from "@/ui-core/cache-data-load-state";

import { Dnevnik } from "@/api/dnevnik";
import type {
    MarkLast,
    MarksSubjectPeriod,
    MarksSubjectFinal,
} from "@/api/dnevnik";

import { CacheManager } from "@/data/cache/cache-manager";
import { useSettingsStore } from "@/stores/settings";

import { Utilities } from "@/utils/utils";

import type { StringResourceKey } from "@/constants/strings";

export class MarksViewModel extends UiViewModel {
    private readonly settingsStore = useSettingsStore();

    private cacheMarksRequestId = 0;
    private cacheFinalMarksRequestId = 0;

    readonly marksData: Ref<UiMarksResult | null> = ref(null);

    readonly marksState: Ref<CacheDataLoadState> = ref(
        CacheDataLoadState.empty(),
    );

    readonly finalMarksState: Ref<CacheDataLoadState> = ref(
        CacheDataLoadState.empty(),
    );

    static readonly CACHE_LAST_MARKS_NAME = "marks";
    static readonly CACHE_SUBJECT_MARKS_PERIOD = "subject_marks_period";
    static readonly CACHE_SUBJECT_MARKS_YEAR = "subject_marks_year";

    resetMarks(): void {
        this.cacheMarksRequestId++;
        this.cacheFinalMarksRequestId++;

        this.cancelRequest("marks");
        this.cancelRequest("finalMarks");

        this.marksState.value = CacheDataLoadState.empty();
        this.finalMarksState.value = CacheDataLoadState.empty();
        this.marksData.value = null;
    }

    doneStudyMarkRating(): void {
        this.settingsStore.studyMarkRating = true;
    }

    doneStudySubjectRating(): void {
        this.settingsStore.studySubjectRating = true;
    }

    async loadCacheMarks(): Promise<void> {
        const requestId = ++this.cacheMarksRequestId;

        this.marksState.value = CacheDataLoadState.cacheLoading();

        const childId = this.settingsStore.activeChildId;

        try {
            const entityLastMarks = await CacheManager.read(
                childId,
                MarksViewModel.CACHE_LAST_MARKS_NAME,
            );

            if (!entityLastMarks) {
                throw new CacheNullException();
            }

            const lastMarks = JSON.parse(
                entityLastMarks.value,
            ) as MarkLast[];

            const entitySubjectMarksPeriod = await CacheManager.read(
                childId,
                MarksViewModel.CACHE_SUBJECT_MARKS_PERIOD,
            );

            if (!entitySubjectMarksPeriod) {
                throw new CacheNullException();
            }

            const subjectMarksPeriod = JSON.parse(
                entitySubjectMarksPeriod.value,
            ) as MarksSubjectPeriod[];

            if (requestId !== this.cacheMarksRequestId) {
                return;
            }

            this.marksData.value = {
                recentMarks: lastMarks,
                periodMarks: subjectMarksPeriod,
                ratingKey: null,
                finalMarks: [],
            };

            this.marksState.value = CacheDataLoadState.cacheSuccess();
        } catch (error: unknown) {
            if (requestId !== this.cacheMarksRequestId) {
                return;
            }

            if (!(error instanceof CacheNullException)) {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Error at loadCacheMarks",
                );

                await CacheManager.writeDnevnikCache(
                    childId,
                    MarksViewModel.CACHE_LAST_MARKS_NAME,
                    "",
                );

                await CacheManager.writeDnevnikCache(
                    childId,
                    MarksViewModel.CACHE_SUBJECT_MARKS_PERIOD,
                    "",
                );
            }

            if (requestId !== this.cacheMarksRequestId) {
                return;
            }

            this.marksState.value = CacheDataLoadState.cacheSuccess();
        }
    }

    loadCloudMarks(): void {
        const childId = this.settingsStore.activeChildId;

        const period = this.settingsStore.lastMarksPeriod;

        void this.executeRequest(
            this.marksState,
            this.marksData,
            "marks",
            "errorMarks" as StringResourceKey,
            () => Dnevnik.getMarks(period),
            (response) => {
                const answer = response.answer;

                if (!answer) {
                    return null;
                }

                return {
                    recentMarks: answer.recentMarks,
                    periodMarks: answer.periodMarks,
                    ratingKey: answer.ratingKey,
                    finalMarks: [],
                };
            },
            async (response) => {
                const answer = response.answer;

                if (!answer) {
                    return;
                }

                await CacheManager.writeDnevnikCache(
                    childId,
                    MarksViewModel.CACHE_LAST_MARKS_NAME,
                    JSON.stringify(answer.recentMarks),
                );

                await CacheManager.writeDnevnikCache(
                    childId,
                    MarksViewModel.CACHE_SUBJECT_MARKS_PERIOD,
                    JSON.stringify(answer.periodMarks),
                );
            },
            {
                key: "marks",
                cancelPrevious: true,
            },
        );
    }

    async loadCacheFinalMarks(): Promise<void> {
        const requestId = ++this.cacheFinalMarksRequestId;

        this.finalMarksState.value = CacheDataLoadState.cacheLoading();

        const childId = this.settingsStore.activeChildId;

        try {
            const entity = await CacheManager.read(
                childId,
                MarksViewModel.CACHE_SUBJECT_MARKS_YEAR,
            );

            if (requestId !== this.cacheFinalMarksRequestId) {
                return;
            }

            if (!entity) {
                throw new CacheNullException();
            }

            const finalMarks = JSON.parse(
                entity.value,
            ) as MarksSubjectFinal[];

            const data = this.marksData.value;

            if (data) {
                this.marksData.value = {
                    ...data,
                    finalMarks,
                };
            }

            this.finalMarksState.value =
                CacheDataLoadState.cacheSuccess();
        } catch (error: unknown) {
            if (!(error instanceof CacheNullException)) {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Error at loadCacheFinalMarks",
                );

                await CacheManager.writeDnevnikCache(
                    childId,
                    MarksViewModel.CACHE_SUBJECT_MARKS_YEAR,
                    "",
                );
            }

            if (requestId !== this.cacheFinalMarksRequestId) {
                return;
            }

            this.finalMarksState.value = CacheDataLoadState.cacheSuccess();
        }
    }

    loadCloudFinalMarks(): void {
        const childId = this.settingsStore.activeChildId;

        void this.executeRequest(
            this.finalMarksState,
            this.marksData,
            "finalMarks",
            "errorMarks" as StringResourceKey,
            () => Dnevnik.getFinalMarks(),
            (response) => {
                const finalMarks = response.answer?.finalMarks;

                if (!finalMarks) {
                    return null;
                }

                const data = this.marksData.value;

                if (!data) {
                    return null;
                }

                return {
                    ...data,
                    finalMarks,
                };
            },
            async (response) => {
                const answer = response.answer;

                if (!answer) {
                    return;
                }

                await CacheManager.writeDnevnikCache(
                    childId,
                    MarksViewModel.CACHE_SUBJECT_MARKS_YEAR,
                    JSON.stringify(answer.finalMarks),
                );
            },
            {
                key: "finalMarks",
                cancelPrevious: true,
            },
        );
    }
}

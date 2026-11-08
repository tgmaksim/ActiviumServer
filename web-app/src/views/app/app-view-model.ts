import type { InjectionKey } from "vue";

import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel from "@/ui-core/ui-view-model";
import { LoadState } from "@/ui-core/load-state";

import { Status, type InformationResult } from "@/api/status";
import { School, type SchoolPostsWithoutVisionResult } from "@/api/school";
import { Ads, type AdResult } from "@/api/ads";

import { strings, type StringResourceKey } from "@/constants/strings";

import { useSettingsStore } from "@/stores/settings";
import { Utilities } from "@/utils/utils";

export class AppViewModel extends UiViewModel {
    readonly infoState: Ref<LoadState<InformationResult>> = ref(
        LoadState.empty(),
    );

    readonly schoolPostsState: Ref<LoadState<SchoolPostsWithoutVisionResult>> = ref(
        LoadState.empty(),
    );

    readonly adState: Ref<LoadState<AdResult>> = ref(
        LoadState.empty(),
    );

    readonly clickAdState: Ref<LoadState<never>> = ref(
        LoadState.empty(),
    );

    private studyTimer: ReturnType<typeof setTimeout> | null = null;

    readonly schoolPostsCount: Ref<number | null> = ref(null);

    private schoolPostsCountRevision = 0;

    private readonly settings = useSettingsStore();

    checkInfoNotifications(): void {
        void this.executeRequest(
            this.infoState,
            "infoNotifications",
            "errorInfoNotifications" as StringResourceKey,
            () => Status.checkInfoNotifications(),
            (response) => response.answer,
            {
                key: "infoNotifications",
                cancelPrevious: true,
            },
        );
    }

    checkNewSchoolPosts(): void {
        const revision = ++this.schoolPostsCountRevision;

        void this.executeRequest(
            this.schoolPostsState,
            "newSchoolPosts",
            "errorNewSchoolPosts" as StringResourceKey,
            () => School.checkNewPosts(),
            (response) => {
                const result = response.answer;

                // Не перезаписываем более актуальное значение,
                // если за время запроса оно уже обновилось через seePost.
                if (revision === this.schoolPostsCountRevision) {
                    this.schoolPostsCount.value = result.countPosts;
                }

                return result;
            },
            {
                key: "schoolPosts",
                cancelPrevious: true,
            },
        );
    }

    /**
     * Обновляет количество неувиденных постов.
     */
    updateSchoolPostsCount(count: number): void {
        if (!Number.isFinite(count)) {
            return;
        }

        // Инвалидируем результат ранее запущенной проверки.
        this.schoolPostsCountRevision++;

        this.schoolPostsCount.value = Math.max(0, Math.trunc(count));
    }

    checkAccessibleAd(): void {
        void this.executeRequest(
            this.adState,
            "checkAccessibleAd",
            "errorAd" as StringResourceKey,
            () => Ads.checkAccessibleAd(),
            (response) => response.answer,
            {
                key: "checkAccessibleAd",
                cancelPrevious: true,
            },
        );
    }

    clickAd(adId: number): void {
        void this.executeRequest(
            this.clickAdState,
            "clickAd",
            "errorClickAd" as StringResourceKey,
            () => Ads.clickAd(adId),
            (response) => response.answer,
            {
                key: "clickAd",
                cancelPrevious: true,
            },
        );
    }

    /**
     * Запускает проверку обучающих подсказок через 10 секунд.
     */
    checkStudy(
        getCurrentRouteName: () => string | symbol | null | undefined,
    ): void {
        if (this.studyTimer !== null) {
            return;
        }

        this.studyTimer = setTimeout(() => {
            this.studyTimer = null;

            this.showStudy(getCurrentRouteName());
        }, 10_000);
    }

    /**
     * Отменяет ожидающую проверку подсказок.
     */
    pauseStudy(): void {
        if (this.studyTimer === null) {
            return;
        }

        clearTimeout(this.studyTimer);
        this.studyTimer = null;
    }

    /**
     * Проверяет необходимость показа обучающей подсказки.
     */
    private showStudy(
        routeName: string | symbol | null | undefined,
    ): void {
        const nowSeconds = Math.floor(Date.now() / 1000);
        const lastStudySeconds = Number(this.settings.lastStudy);

        // С предыдущей подсказки прошло меньше суток.
        if (
            !Number.isFinite(lastStudySeconds) ||
            nowSeconds - lastStudySeconds < 60 * 60 * 24
        ) {
            return;
        }

        let studyText: string | null = null;

        // Страница расписания.
        if (routeName === "schedule") {
            if (!this.settings.studyLessonMenu) {
                studyText = strings.studyLessonMenu;
            }
        }

        // Страница оценок.
        if (routeName === "marks") {
            if (!this.settings.studyMarkRating) {
                studyText = strings.studyMarkRating;
            } else if (!this.settings.studySubjectRating) {
                studyText = strings.studySubjectRating;
            }
        }

        // Подходящей подсказки нет.
        if (studyText === null) {
            return;
        }

        Utilities.showText(studyText, true);

        // Сохраняем время только после показа подсказки.
        this.settings.lastStudy = String(nowSeconds);
    }
}

export const appViewModelKey: InjectionKey<AppViewModel> =
    Symbol("AppViewModel");
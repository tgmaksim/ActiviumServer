import type { InjectionKey } from "vue";

import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel from "@/ui-core/ui-view-model";
import { LoadState } from "@/ui-core/load-state";

import { Status, type InformationResult } from "@/api/status";
import { School, type SchoolPostsWithoutVisionResult } from "@/api/school";
import { Ads, type AdResult } from "@/api/ads";

import type { StringResourceKey } from "@/constants/strings";

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
        void this.executeRequest(
            this.schoolPostsState,
            "newSchoolPosts",
            "errorNewSchoolPosts" as StringResourceKey,
            () => School.checkNewPosts(),
            (response) => response.answer,
            {
                key: "schoolPosts",
                cancelPrevious: true,
            },
        );
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
}

export const appViewModelKey: InjectionKey<AppViewModel> =
    Symbol("AppViewModel");

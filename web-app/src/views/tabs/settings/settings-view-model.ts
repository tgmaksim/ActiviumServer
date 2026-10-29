import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel from "@/ui-core/ui-view-model";
import { LoadState } from "@/ui-core/load-state";

import { Settings } from "@/api/settings";
import { Reviews } from "@/api/reviews";

import type { StringResourceKey } from "@/constants/strings";
import { useSettingsStore } from "@/stores/settings";

// Получаем тип answer непосредственно из возвращаемого API-ответа.
type ApiAnswer<T> = T extends { answer: infer Answer } ? Answer : never;

type ChildrenData = ApiAnswer<
    Awaited<ReturnType<typeof Settings.getChildren>>
>;

type MarksNotificationsData = ApiAnswer<
    Awaited<ReturnType<typeof Settings.getStatusMarksNotifications>>
>;

type EANotificationsData = ApiAnswer<
    Awaited<ReturnType<typeof Settings.getStatusEANotifications>>
>;

type ReviewData = ApiAnswer<
    Awaited<ReturnType<typeof Reviews.getMyReview>>
>;

type ReferralParamsData = ApiAnswer<
    Awaited<ReturnType<typeof Settings.getReferralParams>>
>;

export class SettingsViewModel extends UiViewModel {
    private readonly settingsStore = useSettingsStore();

    readonly childrenState: Ref<LoadState<ChildrenData>> =
        ref(LoadState.empty());

    readonly statusMarksNotificationsState: Ref<
        LoadState<MarksNotificationsData>
    > = ref(LoadState.empty());

    readonly statusEANotificationsState: Ref<
        LoadState<EANotificationsData>
    > = ref(LoadState.empty());

    readonly reviewState: Ref<LoadState<ReviewData>> =
        ref(LoadState.empty());

    readonly referralState: Ref<LoadState<ReferralParamsData>> =
        ref(LoadState.empty());

    loadChildren(): void {
        void this.executeRequest(
            this.childrenState,
            "children",
            "errorChildren" as StringResourceKey,
            () => Settings.getChildren(),
            (response) => response.answer,
            (data) => {
                this.settingsStore.activeChildId = data.activeChildId;
            },
        );
    }

    loadMarksNotifications(): void {
        void this.executeRequest(
            this.statusMarksNotificationsState,
            "marksNotifications",
            "errorMarksNotifications" as StringResourceKey,
            () => Settings.getStatusMarksNotifications(),
            (response) => response.answer,
        );
    }

    loadEANotifications(): void {
        void this.executeRequest(
            this.statusEANotificationsState,
            "eaNotifications",
            "errorEaNotifications" as StringResourceKey,
            () => Settings.getStatusEANotifications(),
            (response) => response.answer,
        );
    }

    switchMarksNotifications(status: boolean): void {
        void this.executeRequest(
            this.statusMarksNotificationsState,
            "switchMarksNotifications",
            "errorMarksNotifications" as StringResourceKey,
            () => Settings.switchMarksNotifications(status),
            () => ({ status }),
        );

        void this.updateFirebaseToken();
    }

    switchEANotifications(status: boolean): void {
        void this.executeRequest(
            this.statusEANotificationsState,
            "switchEANotifications",
            "errorEaNotifications" as StringResourceKey,
            () => Settings.switchEANotifications(status),
            () => ({ status }),
        );

        void this.updateFirebaseToken();
    }

    setActiveChild(childId: number): void {
        if (this.settingsStore.activeChildId === childId) {
            return;
        }

        void this.executeRequest(
            this.childrenState,
            "setActiveChild",
            "errorChildren" as StringResourceKey,
            () => Settings.setActiveChild(childId),
            (response) => response.answer,
            () => {
                this.settingsStore.activeChildId = childId;

                this.loadMarksNotifications();
                this.loadEANotifications();
            },
        );
    }

    loadReview(): void {
        void this.executeRequest(
            this.reviewState,
            "review",
            "errorReview" as StringResourceKey,
            () => Reviews.getMyReview(),
            (response) => response.answer,
        );
    }

    deleteReview(): void {
        void this.executeRequest(
            this.reviewState,
            "deleteReview",
            "errorDeleteReview" as StringResourceKey,
            () => Reviews.deleteReview(),
            () => ({
                review: null,
                onModeration: false,
            }),
        );
    }

    sendReview(stars: number, text: string | null): void {
        void this.executeRequest(
            this.reviewState,
            "sendReview",
            "errorCreateReview" as StringResourceKey,
            () => Reviews.createReview(stars, text),
            (response) => response.answer,
        );
    }

    loadReferralParams(): void {
        void this.executeRequest(
            this.referralState,
            "referralParams",
            "errorReferral" as StringResourceKey,
            () => Settings.getReferralParams(),
            (response) => response.answer,
        );
    }

    private async updateFirebaseToken(): Promise<void> {
        try {
            const token = this.settingsStore.firebaseMessagingToken;

            if (token) {
                await Settings.updateFirebase(token);
            }
        } catch (error: unknown) {

        }
    }
}
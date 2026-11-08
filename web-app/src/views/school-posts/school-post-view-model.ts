import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel from "@/ui-core/ui-view-model";

import {
    LoadState,
} from "@/ui-core";

import {
    setShownError,
} from "@/ui-core/state-utils";

import { School } from "@/api/school";
import type {
    MarkSchoolPostResult,
} from "@/api/school";

import { Utilities } from "@/utils/utils";
import type { StringResourceKey } from "@/constants/strings";

export class SchoolPostViewModel extends UiViewModel {
    private readonly onPostUpdate?: (
        result: MarkSchoolPostResult,
    ) => void;

    readonly viewState: Ref<
        LoadState<MarkSchoolPostResult>
    > = ref(LoadState.empty());

    readonly likeState: Ref<
        LoadState<MarkSchoolPostResult>
    > = ref(LoadState.empty());

    constructor(
        onPostUpdate?: (
            result: MarkSchoolPostResult,
        ) => void,
    ) {
        super();

        this.onPostUpdate = onPostUpdate;
    }

    resetView(): void {
        this.viewState.value = LoadState.empty();
    }

    resetLike(): void {
        this.likeState.value = LoadState.empty();
    }

    resetLikeError(): void {
        setShownError(this.likeState);
    }

    reset(): void {
        this.cancelRequest("viewPost");
        this.cancelRequest("schoolPostLike");

        this.viewState.value = LoadState.empty();
        this.likeState.value = LoadState.empty();
    }

    /**
     * Пометить пост полностью просмотренным.
     */
    async viewPost(postId: number): Promise<void> {
        await this.executeRequest(
            this.viewState,
            "viewPost",
            "errorMarkSchoolPost" as StringResourceKey,
            () => School.viewPost(postId),
            response => response.answer,
            result => {
                this.onPostUpdate?.(result);
            },
            {
                key: "viewPost",
                cancelPrevious: true,
            },
        );
    }

    /**
     * Установить или удалить реакцию.
     */
    async likePost(
        postId: number,
        like: boolean,
    ): Promise<void> {
        await this.executeRequest(
            this.likeState,
            `${like ? "" : "un"}likePost`,
            "errorMarkSchoolPost" as StringResourceKey,
            () => like
                ? School.likePost(postId)
                : School.unlikePost(postId),
            response => response.answer,
            result => {
                this.onPostUpdate?.(result);
            },
            {
                key: "schoolPostLike",
                cancelPrevious: true,
            },
        );
    }
}
import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel, {
    CacheNullException,
} from "@/ui-core/ui-view-model";

import {
    CacheDataLoadState,
    LoadState,
} from "@/ui-core";

import {
    setCacheLoading,
    setCacheSuccess,
    setCacheError,
    setShownCacheError,
    resetMapSuccess,
} from "@/ui-core/state-utils";

import { UiText } from "@/ui-core/ui-text";

import { School } from "@/api/school";
import type {
    SchoolPost,
    SchoolPostsResult,
    MarkSchoolPostResult,
} from "@/api/school";

import { CacheManager } from "@/data/cache/cache-manager";
import { useSettingsStore } from "@/stores/settings";

import { Utilities } from "@/utils/utils";
import type { StringResourceKey } from "@/constants/strings";

export class SchoolViewModel extends UiViewModel {
    private readonly settingsStore = useSettingsStore();

    private cachePostsRequestId = 0;
    private loadingOffset: number | null = null;

    private cacheWriteQueue: Promise<void> = Promise.resolve();

    readonly postsData: Ref<SchoolPostsResult | null> = ref(null);

    readonly postsState: Ref<CacheDataLoadState> = ref(
        CacheDataLoadState.empty(),
    );

    readonly clickPostStates: Ref<
        Map<number, LoadState<MarkSchoolPostResult>>
    > = ref(new Map());

    readonly seePostStates: Ref<
        Map<number, LoadState<MarkSchoolPostResult>>
    > = ref(new Map());

    readonly postsWithoutVision: Ref<number | null> = ref(null);

    static readonly CACHE_POSTS_NAME = "school_posts";

    resetError(): void {
        setShownCacheError(this.postsState);
    }

    resetClickPost(postId: number): void {
        resetMapSuccess(this.clickPostStates, postId);
    }

    resetSeePost(postId: number): void {
        resetMapSuccess(this.seePostStates, postId);
    }

    /**
     * Полный сброс состояния при смене профиля.
     */
    resetPosts(): void {
        this.cachePostsRequestId++;

        this.cancelRequest("schoolPosts");

        for (const postId of this.clickPostStates.value.keys()) {
            this.cancelRequest(`clickPost:${postId}`);
        }

        for (const postId of this.seePostStates.value.keys()) {
            this.cancelRequest(`seePost:${postId}`);
        }

        this.postsData.value = null;
        this.postsState.value = CacheDataLoadState.empty();

        this.clickPostStates.value = new Map();
        this.seePostStates.value = new Map();

        this.loadingOffset = null;
        this.postsWithoutVision.value = null;
    }

    /**
     * Получение постов из локального кэша.
     */
    async loadCachePosts(): Promise<void> {
        const requestId = ++this.cachePostsRequestId;
        const childId = this.settingsStore.activeChildId;

        setCacheLoading(this.postsState);

        try {
            try {
                const entity = await CacheManager.read(
                    childId,
                    SchoolViewModel.CACHE_POSTS_NAME,
                );

                if (!entity) {
                    throw new CacheNullException();
                }

                const posts = JSON.parse(
                    entity.value,
                ) as SchoolPost[];

                if (requestId !== this.cachePostsRequestId) {
                    return;
                }

                this.postsData.value = {
                    classId: 0x4F,
                    posts,
                    nextOffset: null,
                };

                setCacheSuccess(this.postsState);
            } catch (error: unknown) {
                if (requestId !== this.cachePostsRequestId) {
                    return;
                }

                if (!(error instanceof CacheNullException)) {
                    Utilities.log(
                        error instanceof Error
                            ? error
                            : new Error(String(error)),
                        "Error at loadCachePosts",
                    );

                    await this.persistPosts(childId, []);
                }

                if (requestId !== this.cachePostsRequestId) {
                    return;
                }

                this.postsData.value = {
                    classId: 0x4F,
                    posts: [],
                    nextOffset: null,
                };

                setCacheSuccess(this.postsState);
            }
        } catch (error: unknown) {
            if (requestId !== this.cachePostsRequestId) {
                return;
            }

            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Error at loadCachePosts",
            );

            setCacheError(
                this.postsState,
                UiText.stringResource("errorSchoolPosts"),
            );
        }
    }

    /**
     * Получение постов с сервера.
     *
     * offset = 0 — полное обновление списка.
     * offset > 0 — добавление следующей страницы.
     */
    async loadCloudPosts(offset: number = 0): Promise<void> {
        if (this.loadingOffset !== null) {
            return;
        }

        if (
            offset > 0 &&
            (
                !this.postsData.value ||
                this.postsData.value.nextOffset === null
            )
        ) {
            return;
        }

        const childId = this.settingsStore.activeChildId;

        this.loadingOffset = offset;

        try {
            await this.executeRequest(
                this.postsState,
                this.postsData,
                "schoolPosts",
                "errorSchoolPosts" as StringResourceKey,
                () => School.getPosts(offset),
                (response) => {
                    const answer = response.answer;

                    if (!answer) {
                        return null;
                    }

                    if (offset === 0) {
                        return answer;
                    }

                    const currentPosts =
                        this.postsData.value?.posts ?? [];

                    const existingIds = new Set(
                        currentPosts.map(post => post.postId),
                    );

                    return {
                        ...answer,
                        posts: [
                            ...currentPosts,
                            ...answer.posts.filter(
                                post => !existingIds.has(post.postId),
                            ),
                        ],
                    };
                },
                async (response) => {
                    if (!response.answer) {
                        return;
                    }

                    if (childId !== this.settingsStore.activeChildId) {
                        return;
                    }

                    await this.persistPosts(
                        childId,
                        this.postsData.value?.posts ??
                            response.answer.posts,
                    );
                },
                {
                    key: "schoolPosts",
                    cancelPrevious: true,
                },
            );
        } finally {
            if (this.loadingOffset === offset) {
                this.loadingOffset = null;
            }
        }
    }

    /**
     * Отметить пост нажатым.
     */
    async clickPost(postId: number): Promise<void> {
        const childId = this.settingsStore.activeChildId;

        await this.executeRequest(
            this.clickPostStates,
            postId,
            "clickPost",
            "errorMarkSchoolPost" as StringResourceKey,
            () => School.clickPost(postId),
            response => response.answer,
            result => {
                this.updatePostResult(result, childId);
            },
            {
                key: `clickPost:${postId}`,
                cancelPrevious: true,
            },
        );
    }

    /**
     * Отметить пост увиденным.
     */
    async seePost(postId: number): Promise<void> {
        const post = this.postsData.value?.posts.find(
            item => item.postId === postId,
        );

        if (!post || post.isSaw) {
            return;
        }

        const childId = this.settingsStore.activeChildId;

        await this.executeRequest(
            this.seePostStates,
            postId,
            "seePost",
            "errorMarkSchoolPost" as StringResourceKey,
            () => School.seePost(postId),
            response => response.answer,
            result => {
                this.updatePostResult(result, childId);
            },
            {
                key: `seePost:${postId}`,
                cancelPrevious: true,
            },
        );
    }

    /**
     * Обновление поста в текущем списке и локальном кэше.
     */
    updatePost(
        post: SchoolPost,
        childId: number = this.settingsStore.activeChildId,
    ): void {
        if (childId !== this.settingsStore.activeChildId) {
            return;
        }

        const data = this.postsData.value;

        if (!data) {
            return;
        }

        const index = data.posts.findIndex(
            item => item.postId === post.postId,
        );

        if (index === -1) {
            return;
        }

        const posts = [...data.posts];
        posts[index] = post;

        this.postsData.value = {
            ...data,
            posts,
        };

        void this.persistPosts(childId, posts);
    }

    /**
     * Последовательная запись в кэш.
     *
     * Это исключает ситуацию, когда более старый снимок списка
     * завершает запись позже нового.
     */
    private persistPosts(
        childId: number,
        posts: SchoolPost[],
    ): Promise<void> {
        const value = JSON.stringify(posts);

        this.cacheWriteQueue = this.cacheWriteQueue
            .catch(() => {})
            .then(() =>
                CacheManager.writeDnevnikCache(
                    childId,
                    SchoolViewModel.CACHE_POSTS_NAME,
                    value,
                ),
            )
            .catch((error: unknown) => {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Error at persistSchoolPosts",
                );
            });

        return this.cacheWriteQueue;
    }

    updatePostResult(
        result: MarkSchoolPostResult,
        childId: number = this.settingsStore.activeChildId,
    ): void {
        if (childId !== this.settingsStore.activeChildId) {
            return;
        }

        this.postsWithoutVision.value =
            result.countPostsWithoutVision;

        this.updatePost(result.post, childId);
    }
}

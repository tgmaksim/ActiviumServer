import { ref } from "vue";
import type { Ref } from "vue";

import UiViewModel, { CacheNullException } from "@/ui-core/ui-view-model";
import { LoadState } from "@/ui-core/load-state";
import { CacheDataLoadState } from "@/ui-core/cache-data-load-state";

import { Dnevnik } from "@/api/dnevnik";
import type {
    ScheduleDay,
    ScheduleLesson,
} from "@/api/dnevnik";
import { DnevnikTools } from "@/api/dtools";
import type { Note, NoteResult } from "@/api/dtools";
import { School } from "@/api/school";
import type {
    MarkSchoolPostResult,
    SchoolPost,
} from "@/api/school";

import { CacheManager } from "@/data/cache/cache-manager";
import { useSettingsStore } from "@/stores/settings";
import { Utilities } from "@/utils/utils";

import type { StringResourceKey } from "@/constants/strings";

export interface UiScheduleResult {
    schedule: (UiScheduleDay | null)[];
    timezone: number;
    hasAbilityPraise: boolean;
}

export interface UiScheduleDay {
    date: string;
    lessons: UiScheduleLesson[];
    ea: ScheduleDay["ea"];
    schoolPosts: SchoolPost[];
}

export interface UiScheduleLesson {
    lessonKey: string | null;
    number: number;
    subject: string;
    place: string;
    hours: ScheduleLesson["hours"];
    works: ScheduleLesson["works"];
    logs: ScheduleLesson["logs"];
    othersMarks: ScheduleLesson["othersMarks"];
    avgGroupLessonMark: ScheduleLesson["avgGroupLessonMark"];
    homework: string | null;
    note: Note | null;
    files: ScheduleLesson["files"];
    ratingKey: string | null;
    dnevnikruUrl: string | null;
    praiseState: LoadState<never> | null;
    noteState: LoadState<NoteResult> | null;
    isExtra: boolean;
}

type PraiseData = Record<string, never>;

export class ScheduleViewModel extends UiViewModel {
    private readonly settingsStore = useSettingsStore();

    private cacheScheduleRequestId = 0;

    readonly scheduleData: Ref<UiScheduleResult | null> = ref(null);

    readonly scheduleState: Ref<CacheDataLoadState> = ref(
        CacheDataLoadState.empty(),
    );

    readonly praiseStates: Ref<Map<string, LoadState<PraiseData>>> = ref(
        new Map(),
    );

    readonly noteStates: Ref<Map<string, LoadState<NoteResult>>> = ref(
        new Map(),
    );

    readonly seePostStates: Ref<
        Map<number, LoadState<MarkSchoolPostResult>>
    > = ref(new Map());

    readonly clickPostStates: Ref<
        Map<number, LoadState<MarkSchoolPostResult>>
    > = ref(new Map());

    static readonly CACHE_SCHEDULE_NAME = "schedule";

    static readonly CACHE_TIMEZONE_NAME = "timezone";

    resetSchedule(): void {
        this.cacheScheduleRequestId++;

        this.scheduleState.value = CacheDataLoadState.empty();
        this.scheduleData.value = null;
    }

    emptyStates(): void {
        this.praiseStates.value = new Map();
        this.noteStates.value = new Map();
    }

    doneStudyLessonMenu(): void {
        this.settingsStore.studyLessonMenu = true;
    }

    async loadCacheSchedule(): Promise<void> {
        const requestId = ++this.cacheScheduleRequestId;

        this.scheduleState.value = CacheDataLoadState.cacheLoading();

        const before = this.settingsStore.beforeSchedule;
        const after = this.settingsStore.afterSchedule;
        const totalDays = before + 1 + after;
        const childId = this.settingsStore.activeChildId;

        try {
            const timezoneEntry = await CacheManager.read(
                childId,
                ScheduleViewModel.CACHE_TIMEZONE_NAME,
            );

            if (!timezoneEntry) {
                throw new CacheNullException();
            }

            const timezone = Number.parseInt(timezoneEntry.value, 10);

            if (!Number.isFinite(timezone)) {
                throw new Error("Invalid cached timezone");
            }

            const entity = await CacheManager.read(
                childId,
                ScheduleViewModel.CACHE_SCHEDULE_NAME,
            );

            if (!entity) {
                throw new CacheNullException();
            }

            const schedule = JSON.parse(entity.value) as ScheduleDay[];
            const hasAbilityPraise = false;

            if (requestId !== this.cacheScheduleRequestId) {
                return;
            }

            this.scheduleData.value = {
                schedule: this.normalizeSchedule(
                    schedule,
                    before,
                    after,
                    timezone,
                    hasAbilityPraise,
                ),
                timezone,
                hasAbilityPraise,
            };

            this.scheduleState.value = CacheDataLoadState.cacheSuccess();
        } catch (error: unknown) {
            if (requestId !== this.cacheScheduleRequestId) {
                return;
            }

            if (error instanceof CacheNullException) {
                // Кэш отсутствует.
            } else {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Error at loadCacheSchedule",
                );

                await CacheManager.writeDnevnikCache(
                    childId,
                    ScheduleViewModel.CACHE_SCHEDULE_NAME,
                    "",
                );
            }

            this.scheduleData.value = {
                schedule: Array.from(
                    { length: totalDays },
                    () => null,
                ),
                timezone: 0,
                hasAbilityPraise: false,
            };

            this.scheduleState.value = CacheDataLoadState.cacheSuccess();
        }
    }

    private normalizeSchedule(
        schedule: ScheduleDay[],
        before: number,
        after: number,
        timezone: number,
        hasAbilityPraise: boolean,
    ): (UiScheduleDay | null)[] {
        const currentDate = this.todayInTimezone(timezone);
        const firstDate = new Date(currentDate);

        firstDate.setUTCDate(firstDate.getUTCDate() - before);

        const byDate = new Map(
            schedule.map((day) => [day.date, day]),
        );

        const days: (UiScheduleDay | null)[] = [];

        for (let i = 0; i < before + 1 + after; i++) {
            const date = new Date(firstDate);
            date.setUTCDate(date.getUTCDate() + i);

            const dateString = this.formatDate(date);
            const day = byDate.get(dateString);

            if (!day) {
                days.push(null);
                continue;
            }

            const praiseState = hasAbilityPraise
                ? LoadState.empty()
                : null;

            days.push(this.toUi(day, praiseState));
        }

        return days;
    }

    private todayInTimezone(offsetSeconds: number): Date {
        return new Date(Date.now() + offsetSeconds * 1000);
    }

    private formatDate(date: Date): string {
        const year = date.getUTCFullYear();
        const month = String(date.getUTCMonth() + 1).padStart(2, "0");
        const day = String(date.getUTCDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    }

    private toUi(
        day: ScheduleDay,
        praiseState: LoadState<never> | null,
    ): UiScheduleDay {
        return {
            date: day.date,
            lessons: day.lessons.map((lesson) => ({
                lessonKey: lesson.lessonKey,
                number: lesson.number,
                subject: lesson.subject,
                place: lesson.place,
                hours: lesson.hours,
                works: lesson.works,
                logs: lesson.logs,
                othersMarks: lesson.othersMarks,
                avgGroupLessonMark: lesson.avgGroupLessonMark,
                homework: lesson.homework,
                note: lesson.note,
                files: lesson.files,
                ratingKey: lesson.ratingKey,
                dnevnikruUrl: lesson.dnevnikruUrl,
                praiseState,
                noteState: null,
                isExtra: false,
            })),
            ea: day.ea,
            schoolPosts: day.schoolPosts,
        };
    }

    loadCloudSchedule(): void {
        const childId = this.settingsStore.activeChildId;
        const before = this.settingsStore.beforeSchedule;
        const after = this.settingsStore.afterSchedule;

        void this.executeRequest(
            this.scheduleState,
            this.scheduleData,
            "schedule",
            "errorSchedule" as StringResourceKey,
            () => Dnevnik.getSchedule(before, after),
            (response) => {
                const answer = response.answer;

                if (!answer) {
                    return null;
                }

                return {
                    schedule: this.normalizeSchedule(
                        answer.schedule,
                        before,
                        after,
                        answer.timezone,
                        answer.hasAbilityPraise,
                    ),
                    timezone: answer.timezone,
                    hasAbilityPraise: answer.hasAbilityPraise,
                };
            },
            async (response) => {
                const answer = response.answer;

                if (!answer) {
                    return;
                }

                await CacheManager.writeDnevnikCache(
                    childId,
                    ScheduleViewModel.CACHE_TIMEZONE_NAME,
                    answer.timezone.toString(),
                );

                await CacheManager.writeDnevnikCache(
                    childId,
                    ScheduleViewModel.CACHE_SCHEDULE_NAME,
                    JSON.stringify(answer.schedule),
                );
            },
            {
                key: "schedule",
                cancelPrevious: true,
            },
        );
    }

    sendPraise(lessonKey: string, text: string | null): void {
        void this.executeRequest(
            this.praiseStates,
            lessonKey,
            "praise",
            "errorPraise" as StringResourceKey,
            () => DnevnikTools.sendPraise(lessonKey, null, text),
            () => ({}),
        );
    }

    createLessonNote(
        lessonKey: string,
        text: string,
        public_: boolean,
        remindTime: string | null,
    ): void {
        void this.executeRequest(
            this.noteStates,
            lessonKey,
            "note",
            "errorNote" as StringResourceKey,
            () => DnevnikTools.createNote(
                lessonKey,
                text,
                public_,
                remindTime,
            ),
            (response) => response.answer,
            (noteResult) => this.onSuccessEditLessonNote(
                lessonKey,
                noteResult,
            ),
        );
    }

    deleteLessonNote(lessonKey: string): void {
        void this.executeRequest(
            this.noteStates,
            lessonKey,
            "deleteNote",
            "errorDeleteNote" as StringResourceKey,
            () => DnevnikTools.deleteNote(lessonKey),
            () => ({
                classId: 0x4B,
                note: null,
            }),
            (noteResult) => this.onSuccessEditLessonNote(
                lessonKey,
                noteResult,
            ),
        );
    }

    private async onSuccessEditLessonNote(
        lessonKey: string,
        noteResult: NoteResult,
    ): Promise<void> {
        const data = this.scheduleData.value;

        if (data) {
            this.scheduleData.value = {
                ...data,
                schedule: data.schedule.map((day) => {
                    if (!day?.lessons.some(
                        (lesson) => lesson.lessonKey === lessonKey,
                    )) {
                        return day;
                    }

                    return {
                        ...day,
                        lessons: day.lessons.map((lesson) => (
                            lesson.lessonKey === lessonKey
                                ? { ...lesson, note: noteResult.note }
                                : lesson
                        )),
                    };
                }),
            };
        }

        try {
            const childId = this.settingsStore.activeChildId;

            const entity = await CacheManager.read(
                childId,
                ScheduleViewModel.CACHE_SCHEDULE_NAME,
            );

            if (!entity) {
                throw new CacheNullException();
            }

            const schedule = JSON.parse(entity.value) as ScheduleDay[];

            const newSchedule = schedule.map((day) => {
                if (!day.lessons.some(
                    (lesson) => lesson.lessonKey === lessonKey,
                )) {
                    return day;
                }

                return {
                    ...day,
                    lessons: day.lessons.map((lesson) => (
                        lesson.lessonKey === lessonKey
                            ? { ...lesson, note: noteResult.note }
                            : lesson
                    )),
                };
            });

            await CacheManager.writeDnevnikCache(
                childId,
                ScheduleViewModel.CACHE_SCHEDULE_NAME,
                JSON.stringify(newSchedule),
            );
        } catch (error: unknown) {
            if (error instanceof CacheNullException) {
                return;
            }

            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Error at onSuccessEditLessonNote",
            );
        }
    }

    seePost(postId: number): void {
        void this.executeRequest(
            this.seePostStates,
            postId,
            "seePost",
            "errorMarkSchoolPost" as StringResourceKey,
            () => School.seePost(postId),
            (response) => response.answer,
        );
    }

    clickPost(postId: number): void {
        void this.executeRequest(
            this.clickPostStates,
            postId,
            "clickPost",
            "errorMarkSchoolPost" as StringResourceKey,
            () => School.clickPost(postId),
            (response) => response.answer,
            (postResult) => this.onSuccessUpdatePost(
                postId,
                postResult,
            ),
        );
    }

    updatePost(
        postId: number,
        postResult: MarkSchoolPostResult,
    ): void {
        const data = this.scheduleData.value;

        if (!data) {
            return;
        }

        this.scheduleData.value = {
            ...data,
            schedule: data.schedule.map((day) => {
                if (!day?.schoolPosts.some(
                    (post) => post.postId === postId,
                )) {
                    return day;
                }

                return {
                    ...day,
                    schoolPosts: day.schoolPosts.map((post) => (
                        post.postId === postId
                            ? postResult.post
                            : post
                    )),
                };
            }),
        };
    }

    private async onSuccessUpdatePost(
        postId: number,
        postResult: MarkSchoolPostResult,
    ): Promise<void> {
        this.updatePost(postId, postResult);

        try {
            const childId = this.settingsStore.activeChildId;

            const entity = await CacheManager.read(
                childId,
                ScheduleViewModel.CACHE_SCHEDULE_NAME,
            );

            if (!entity) {
                throw new CacheNullException();
            }

            const schedule = JSON.parse(entity.value) as ScheduleDay[];

            const newSchedule = schedule.map((day) => {
                if (!day.schoolPosts.some(
                    (post) => post.postId === postId,
                )) {
                    return day;
                }

                return {
                    ...day,
                    schoolPosts: day.schoolPosts.map((post) => (
                        post.postId === postId
                            ? postResult.post
                            : post
                    )),
                };
            });

            await CacheManager.writeDnevnikCache(
                childId,
                ScheduleViewModel.CACHE_SCHEDULE_NAME,
                JSON.stringify(newSchedule),
            );
        } catch (error: unknown) {
            if (error instanceof CacheNullException) {
                return;
            }

            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Error at onSuccessUpdatePost",
            );
        }
    }
}
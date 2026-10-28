<template>
    <div class="settings-page">
        <section class="settings-card">
            <h2 class="section-title">
                {{ strings.settings }}
            </h2>

            <label class="setting-row">
                <span class="setting-description">
                    {{ strings.settingsTheme }}
                </span>

                <input
                    v-model="settings.darkTheme"
                    class="switch"
                    type="checkbox"
                    @change="applyTheme"
                />
            </label>

            <div>
                <div class="setting-heading">
                    <span
                        v-if="eaNotificationsLoading"
                        class="loader"
                        aria-label="Loading"
                    ></span>
                </div>

                <label
                    v-if="eaNotificationsLoaded || eaNotificationsError"
                    class="setting-row setting-row-nested"
                >
                    <span class="setting-description">
                        {{ strings.settingsEaNotifications }}
                    </span>

                    <input
                        v-if="eaNotificationsLoaded"
                        v-model="eaNotifications"
                        class="switch"
                        type="checkbox"
                        :disabled="eaNotificationsBusy"
                        @change="toggleEaNotifications"
                    />

                    <button
                        v-else
                        class="setting-error-button"
                        type="button"
                        :aria-label="strings.errorEaNotifications"
                        @click="loadEaNotifications"
                    >
                        ×
                    </button>
                </label>
            </div>

            <div>
                <div class="setting-heading">
                    <span
                        v-if="marksNotificationsLoading"
                        class="loader"
                        aria-label="Loading"
                    ></span>
                </div>

                <label
                    v-if="marksNotificationsLoaded || marksNotificationsError"
                    class="setting-row setting-row-nested"
                >
                    <span class="setting-description">
                        {{ strings.settingsMarksNotifications }}
                    </span>

                    <input
                        v-if="marksNotificationsLoaded"
                        v-model="marksNotifications"
                        class="switch"
                        type="checkbox"
                        :disabled="marksNotificationsBusy"
                        @change="toggleMarksNotifications"
                    />

                    <button
                        v-else
                        class="setting-error-button"
                        type="button"
                        :aria-label="strings.errorMarksNotifications"
                        @click="loadMarksNotifications"
                    >
                        ×
                    </button>
                </label>
            </div>

            <label class="setting-row">
                <span class="setting-description">
                    {{ strings.settingsShowNullSubjectMarks }}
                </span>

                <input
                    v-model="settings.showNullSubjectMarks"
                    class="switch"
                    type="checkbox"
                />
            </label>

            <div class="setting-range-block">
                <div class="setting-heading">
                    <span class="setting-description">
                        {{ strings.settingsSchedulePeriod }}
                    </span>
                </div>

                <div
                    class="range-control"
                    :class="{ 'range-control-active': activeScheduleThumb !== null }"
                >
                    <div class="range-track" aria-hidden="true">
                        <span
                            class="range-track-selected"
                            :style="scheduleTrackStyle"
                        ></span>
                    </div>

                    <div
                        v-if="activeScheduleThumb !== null"
                        class="slider-island"
                        :style="scheduleLabelStyle(activeScheduleThumb)"
                        aria-live="polite"
                    >
                        {{ scheduleLabel(activeScheduleThumb === 'left' ? scheduleLeft : scheduleRight) }}
                    </div>

                    <input
                        v-model.number="scheduleLeft"
                        class="range-input range-input-left"
                        type="range"
                        min="-14"
                        max="21"
                        step="1"
                        aria-label="Начало диапазона расписания"
                        @pointerdown="activeScheduleThumb = 'left'"
                        @pointerup="finishScheduleRange"
                        @pointercancel="finishScheduleRange"
                        @focus="activeScheduleThumb = 'left'"
                        @blur="activeScheduleThumb = null"
                        @input="updateScheduleRange('left')"
                        @change="saveScheduleRange"
                    />

                    <input
                        v-model.number="scheduleRight"
                        class="range-input range-input-right"
                        type="range"
                        min="-14"
                        max="21"
                        step="1"
                        aria-label="Конец диапазона расписания"
                        @pointerdown="activeScheduleThumb = 'right'"
                        @pointerup="finishScheduleRange"
                        @pointercancel="finishScheduleRange"
                        @focus="activeScheduleThumb = 'right'"
                        @blur="activeScheduleThumb = null"
                        @input="updateScheduleRange('right')"
                        @change="saveScheduleRange"
                    />
                </div>

                <p
                    v-if="scheduleWarning"
                    class="setting-warning"
                >
                    {{ strings.settingsScheduleWarning }}
                </p>
            </div>

            <div class="setting-range-block">
                <div class="setting-heading">
                    <span class="setting-description">
                        {{ strings.settingsLastMarksPeriod }}
                    </span>
                </div>

                <div
                    class="single-range-control"
                    :class="{ 'range-control-active': lastMarksSliderActive }"
                >
                    <div class="range-track" aria-hidden="true">
                        <span
                            class="range-track-selected"
                            :style="lastMarksTrackStyle"
                        ></span>
                    </div>

                    <div
                        v-if="lastMarksSliderActive"
                        class="slider-island"
                        :style="lastMarksLabelStyle"
                        aria-live="polite"
                    >
                        {{ strings.lastMarksLabel(lastMarksPeriod) }}
                    </div>

                    <input
                        v-model.number="lastMarksPeriod"
                        class="single-range"
                        type="range"
                        min="0"
                        max="14"
                        step="1"
                        :aria-label="strings.settingsLastMarksPeriod"
                        @pointerdown="lastMarksSliderActive = true"
                        @pointerup="finishLastMarksSlider"
                        @pointercancel="finishLastMarksSlider"
                        @focus="lastMarksSliderActive = true"
                        @blur="lastMarksSliderActive = false"
                        @input="normalizeLastMarksPeriod"
                        @change="saveLastMarksPeriod"
                    />
                </div>

                <p
                    v-if="lastMarksPeriod > 7"
                    class="setting-warning"
                >
                    {{ strings.settingsLastMarksWarning }}
                </p>
            </div>
        </section>

        <section class="settings-card">
            <button
                class="section-heading-button"
                type="button"
                :aria-expanded="childrenExpanded"
                @click="childrenExpanded = !childrenExpanded"
            >
                <span class="section-title">
                    {{ strings.activeProfile }}
                </span>
                <span class="section-chevron" aria-hidden="true">
                    {{ childrenExpanded ? "−" : "+" }}
                </span>
            </button>

            <div
                v-if="!childrenLoading && !childrenError && activeChild"
                class="child-option child-option-active"
                aria-current="true"
            >
                <span>{{ activeChild.name }}</span>
                <span class="child-active">
                    {{ strings.selectedProfile }}
                </span>
            </div>

            <p
                v-if="childrenLoading"
                class="state-message"
            >
                <span class="loader"></span>
            </p>

            <p v-else-if="childrenError" class="state-message">
                <button
                    class="setting-error-button"
                    type="button"
                    :aria-label="strings.errorChildren"
                    @click="loadChildren"
                >
                    ×
                </button>
            </p>

            <template v-else-if="childrenExpanded">
                <p
                    v-if="children.length === 0"
                    class="state-message"
                >
                    {{ strings.noChild }}
                </p>

                <button
                    v-for="child in otherChildren"
                    :key="child.id"
                    class="child-option"
                    type="button"
                    :disabled="
                        child.id === activeChildId ||
                        activeChildBusy
                    "
                    @click="selectChild(child)"
                >
                    <span>{{ child.name }}</span>

                    <span
                        v-if="child.id === activeChildId"
                        class="child-active"
                    >
                        {{ strings.selectedProfile }}
                    </span>
                </button>
            </template>
        </section>

        <section class="settings-card">
            <h2 class="section-title">
                {{ strings.review }}
            </h2>

            <div
                v-if="reviewLoading"
                class="state-message"
            >
                <span class="loader"></span>
            </div>

            <div v-else-if="reviewError" class="state-message">
                <button
                    class="setting-error-button"
                    type="button"
                    :aria-label="strings.errorReview"
                    @click="loadReview"
                >
                    ×
                </button>
            </div>

            <template v-else-if="myReview">
                <span class="review-status">
                    {{
                        strings.reviewMeta(
                            myReview.name,
                            new Intl.DateTimeFormat('ru-RU', {day: '2-digit', month: '2-digit', year: 'numeric'}).format(new Date(myReview.createdAt)),
                            (myReview.isUpdated ? strings.reviewEditMarker : '') +
                                (myReviewOnModeration ? strings.reviewModerationMarker : '')
                        )
                    }}
                </span>

                <div class="review-meta">
                    <span
                        v-for="star in 5"
                        :key="star"
                        class="review-star"
                        :class="{ 'review-star-filled': star <= reviewStars }"
                    >
                        ★
                    </span>
                </div>

                <p class="review-text">
                    {{ myReview.text }}
                </p>

                <p class="review-likes">
                    👍 {{ myReview.likes }}
                </p>

                <button
                    class="action-button"
                    type="button"
                    @click="openReviewEditor"
                >
                    {{ strings.editReview }}
                </button>

                <button
                    class="action-button action-button-secondary"
                    type="button"
                    :disabled="reviewActionBusy"
                    @click="showDeleteReviewDialog = true"
                >
                    {{ strings.deleteReview }}
                </button>
            </template>

            <button
                v-else
                class="action-button"
                type="button"
                @click="openReviewEditor"
            >
                {{ strings.writeReview }}
            </button>

            <button
                class="action-button action-button-secondary"
                type="button"
                @click="openAllReviews"
            >
                {{ strings.openAllReviews }}
            </button>
        </section>

        <section class="settings-card">
            <h2 class="section-title">
                {{ strings.referral }}
            </h2>

            <p
                v-if="referralLoading"
                class="state-message"
            >
                <span class="loader"></span>
            </p>

            <div v-else-if="referralError" class="state-message">
                <button
                    class="setting-error-button"
                    type="button"
                    :aria-label="strings.errorReferral"
                    @click="loadReferral"
                >
                    ×
                </button>
            </div>

            <template v-else-if="referral">
                <p v-if="referral.meReferralName">
                    {{ strings.meReferral(referral.meReferralName) }}
                </p>

                <p>
                    {{ strings.referralCount(referral.referralsCount) }}
                </p>

                <p>
                    {{
                        referral.countActiveRelatives == referral.countRelatives
                            ? (referral.isParent
                                ? strings.allActiveRelativesChildren
                                : strings.allActiveRelativesParents)
                            : (referral.isParent
                                ? strings.activeRelativesChildren(referral.countActiveRelatives, referral.countRelatives)
                                : strings.activeRelativesParents(referral.countActiveRelatives, referral.countRelatives))
                    }}
                </p>

                <button
                    class="action-button"
                    type="button"
                    @click="shareReferral"
                >
                    {{ strings.share }}
                </button>
            </template>
        </section>

        <section class="settings-card">
            <h2 class="section-title">
                {{ strings.account }}
            </h2>

            <p class="about-description">
                {{ strings.accountInfo }}
            </p>

            <button
                class="action-button"
                type="button"
                @click="showLogoutDialog = true"
            >
                {{ strings.logout }}
            </button>
        </section>

        <section class="settings-card">
            <h2 class="section-title">
                {{ strings.about }}
            </h2>

            <p class="about-description">
                {{ strings.appInfo }}
            </p>

            <button
                class="action-button"
                type="button"
                @click="openSite"
            >
                {{ strings.openSite }}
            </button>
        </section>

        <section class="settings-card about-meta">
            <p>
                {{ strings.version(APP_VERSION, APP_VERSION_CODE) }}
            </p>

            <p>
                {{ deviceInfo }}
            </p>

            <p>
                {{ strings.developer }}
            </p>
        </section>

        <AppDialog
            :visible="showDeleteReviewDialog"
            :title="strings.deleteReview"
            :message="strings.messageDialogDeleteReview"
            :action-text="strings.buttonDialogDeleteReview"
            :cancel-text="strings.cancel"
            :loading="reviewActionBusy"
            @action="deleteMyReview"
            @cancel="showDeleteReviewDialog = false"
        />

        <ReviewEditorDialog
            :visible="showReviewEditor"
            :editing="editingReview"
            :initial-stars="reviewStars"
            :initial-text="myReview?.text ?? ''"
            @close="showReviewEditor = false"
            @submit="submitReview"
        />

        <AppDialog
            :visible="showLogoutDialog"
            :title="strings.logout"
            :message="strings.logout"
            :action-text="strings.logout"
            :cancel-text="strings.cancel"
            @action="confirmLogout"
            @cancel="showLogoutDialog = false"
        />

        <AppDialog
            :visible="showMessageDialog"
            :title="messageDialogTitle"
            :message="messageDialogText"
            :action-text="strings.ok"
            @action="showMessageDialog = false"
            @cancel="showMessageDialog = false"
        />
    </div>
</template>

<script setup lang="ts">
import {
    computed,
    onMounted,
    ref,
    watch,
} from "vue";

import AppDialog from "@/components/AppDialog.vue";
import { strings } from "@/constants/strings";
import { Settings } from "@/api/settings";
import { Reviews } from "@/api/reviews";
import { NotificationPermission } from "@/notifications/permission";
import { useSettingsStore } from "@/stores/settings";
import { logout } from "@/utils/logout";
import { Utilities } from "@/utils/utils";
import ReviewEditorDialog from "@/components/ReviewEditorDialog.vue";

import { getDeviceInfo } from "@/utils/device";
import { APP_VERSION, APP_VERSION_CODE } from "@/constants/app";

const deviceInfo = getDeviceInfo();

interface Child {
    id: number;
    name: string;
    [key: string]: unknown;
}

interface MyReview {
    reviewId: number;
    stars: number;
    text: string;
    likes: number;
    isUpdated: boolean;
    createdAt: string;
    [key: string]: unknown;
}

interface ReferralParams {
    meReferralName: string | null;
    referralsCount: number;
    isParent: boolean;
    countActiveRelatives: number;
    countRelatives: number;
    referralUrl: string;
}

const settings = useSettingsStore();

const scheduleLeft = ref(-settings.beforeSchedule);
const scheduleRight = ref(settings.afterSchedule);
const lastMarksPeriod = ref(settings.lastMarksPeriod);

const activeScheduleThumb = ref<"left" | "right" | null>(null);
const lastMarksSliderActive = ref(false);

const scheduleRangeText = computed(() => {
    const before = Math.abs(scheduleLeft.value);
    const after = scheduleRight.value;

    return `${before} / ${after}`;
});

const scheduleTrackStyle = computed(() => {
    const min = -14;
    const max = 21;
    const left = ((scheduleLeft.value - min) / (max - min)) * 100;
    const right = ((scheduleRight.value - min) / (max - min)) * 100;

    return {
        left: `${left}%`,
        width: `${Math.max(0, right - left)}%`,
    };
});

const activeChild = computed(
    () => children.value.find((child) => child.id === activeChildId.value) ?? null,
);

const otherChildren = computed(
    () => children.value.filter((child) => child.id !== activeChildId.value),
);

const lastMarksLabelStyle = computed(() => ({
    left: `${(lastMarksPeriod.value / 14) * 100}%`,
}));

const lastMarksTrackStyle = computed(() => ({
    left: "0%",
    width: `${(lastMarksPeriod.value / 14) * 100}%`,
}));

function scheduleLabel(value: number): string {
    if (value < 0) {
        return strings.scheduleRangeLabelFrom(Math.abs(value));
    }

    if (value === 0) {
        return strings.scheduleRangeLabelToday;
    }

    if (value === 1) {
        return strings.scheduleRangeLabelTomorrow;
    }

    return strings.scheduleRangeLabelTo(value);
}

function scheduleLabelStyle(thumb: "left" | "right") {
    const value = thumb === "left" ? scheduleLeft.value : scheduleRight.value;
    const position = ((value + 14) / 35) * 100;

    return {
        left: `${Math.min(100, Math.max(0, position))}%`,
    };
}

function finishScheduleRange(): void {
    saveScheduleRange();
    activeScheduleThumb.value = null;
}

function normalizeLastMarksPeriod(): void {
    if (lastMarksPeriod.value < 1) {
        lastMarksPeriod.value = 1;
    }
}

function finishLastMarksSlider(): void {
    saveLastMarksPeriod();
    lastMarksSliderActive.value = false;
}

const scheduleWarning = computed(() =>
    Math.abs(scheduleLeft.value) > 7 ||
    scheduleRight.value > 14,
);

const marksNotifications = ref(false);
const marksNotificationsLoading = ref(true);
const marksNotificationsLoaded = ref(false);
const marksNotificationsBusy = ref(false);
const marksNotificationsError = ref(false);

const eaNotifications = ref(false);
const eaNotificationsLoading = ref(true);
const eaNotificationsLoaded = ref(false);
const eaNotificationsBusy = ref(false);
const eaNotificationsError = ref(false);

const children = ref<Child[]>([]);
const activeChildId = ref(settings.activeChildId);
const childrenExpanded = ref(false);
const childrenLoading = ref(true);
const childrenError = ref(false);
const activeChildBusy = ref(false);

const reviewLoading = ref(true);
const reviewError = ref(false);
const reviewActionBusy = ref(false);
const myReview = ref<MyReview | null>(null);
const myReviewOnModeration = ref<boolean | null>(null);

const showReviewEditor = ref(false);
const editingReview = ref(false);

const showDeleteReviewDialog = ref(false);
const showLogoutDialog = ref(false);

const referralLoading = ref(true);
const referralError = ref(false);
const referral = ref<ReferralParams | null>(null);

const showMessageDialog = ref(false);
const messageDialogTitle = ref("");
const messageDialogText = ref("");

const reviewStars = computed(
    () => Number(myReview.value?.stars ?? myReview.value?.rating ?? 0),
);

watch(
    () => settings.darkTheme,
    (darkTheme) => {
        document.documentElement.classList.toggle("dark", darkTheme);
    },
    { immediate: true },
);

watch(
    () => settings.beforeSchedule,
    (value) => {
        scheduleLeft.value = -value;
    },
);

watch(
    () => settings.afterSchedule,
    (value) => {
        scheduleRight.value = value;
    },
);

watch(
    () => settings.lastMarksPeriod,
    (value) => {
        lastMarksPeriod.value = value;
    },
);

function applyTheme(): void {
    document.documentElement.classList.toggle(
        "dark",
        settings.darkTheme,
    );
}

function updateScheduleRange(changed: "left" | "right"): void {
    if (scheduleRight.value - scheduleLeft.value > 30) {
        if (changed === "left") {
            scheduleLeft.value = scheduleRight.value - 30;
        } else {
            scheduleRight.value = scheduleLeft.value + 30;
        }
    }

    scheduleLeft.value = Math.max(-14, Math.min(0, scheduleLeft.value));
    scheduleRight.value = Math.max(1, Math.min(21, scheduleRight.value));
}

function saveScheduleRange(): void {
    const before = Math.abs(scheduleLeft.value);
    const after = scheduleRight.value;

    if (before + after > 30) {
        return;
    }

    settings.beforeSchedule = before;
    settings.afterSchedule = after;
}

function saveLastMarksPeriod(): void {
    const value = Math.max(1, Math.min(14, lastMarksPeriod.value));
    lastMarksPeriod.value = value;
    settings.lastMarksPeriod = value;
}

function showMessage(title: string, message: string): void {
    messageDialogTitle.value = title;
    messageDialogText.value = message;
    showMessageDialog.value = true;
}

function getAnswer<T>(response: unknown): T | null {
    if (!response || typeof response !== "object") {
        return null;
    }

    const value = response as {
        status?: boolean;
        answer?: T | null;
        error?: { errorMessage?: string };
    };

    if (value.status === false) {
        throw new Error(value.error?.errorMessage || strings.errorApi);
    }

    return value.answer ?? null;
}

async function loadMarksNotifications(): Promise<void> {
    marksNotificationsLoading.value = true;
    marksNotificationsError.value = false;
    marksNotificationsLoaded.value = false;

    try {
        const answer = getAnswer<{
            status?: boolean;
        }>(await Settings.getStatusMarksNotifications());

        if (!answer || typeof answer.status !== "boolean") {
            throw new Error(strings.errorMarksNotifications);
        }

        marksNotifications.value = answer.status;
        marksNotificationsLoaded.value = true;
    } catch (error) {
        Utilities.log(error);
        marksNotificationsError.value = true;
        Utilities.showText(strings.errorMarksNotifications);
    } finally {
        marksNotificationsLoading.value = false;
    }
}

async function toggleMarksNotifications(): Promise<void> {
    const desired = marksNotifications.value;
    const previous = !desired;

    marksNotificationsBusy.value = true;

    try {
        if (desired) {
            const permission = await NotificationPermission.checkPermission();

            if (permission !== "granted") {
                const result = await NotificationPermission.enableNotifications();

                if (result !== "enabled") {
                    throw new Error(strings.errorMarksNotifications);
                }
            }
        }

        getAnswer(
            await Settings.switchMarksNotifications(desired),
        );
    } catch (error) {
        Utilities.log(error);
        marksNotifications.value = previous;
        Utilities.showText(strings.errorMarksNotifications);
    } finally {
        marksNotificationsBusy.value = false;
    }
}

async function loadEaNotifications(): Promise<void> {
    eaNotificationsLoading.value = true;
    eaNotificationsError.value = false;
    eaNotificationsLoaded.value = false;

    try {
        const answer = getAnswer<{
            status?: boolean;
        }>(await Settings.getStatusEANotifications());

        if (!answer || typeof answer.status !== "boolean") {
            throw new Error(strings.errorEaNotifications);
        }

        eaNotifications.value = answer.status;
        eaNotificationsLoaded.value = true;
    } catch (error) {
        Utilities.log(error);
        eaNotificationsError.value = true;
        Utilities.showText(strings.errorEaNotifications);
    } finally {
        eaNotificationsLoading.value = false;
    }
}

async function toggleEaNotifications(): Promise<void> {
    const desired = eaNotifications.value;
    const previous = !desired;

    eaNotificationsBusy.value = true;

    try {
        if (desired) {
            const permission = await NotificationPermission.checkPermission();

            if (permission !== "granted") {
                const result = await NotificationPermission.enableNotifications();

                if (result !== "enabled") {
                    throw new Error(strings.errorEaNotifications);
                }
            }
        }

        getAnswer(
            await Settings.switchEANotifications(desired),
        );
    } catch (error) {
        Utilities.log(error);
        eaNotifications.value = previous;
        Utilities.showText(strings.errorEaNotifications);
    } finally {
        eaNotificationsBusy.value = false;
    }
}

async function loadChildren(): Promise<void> {
    childrenLoading.value = true;
    childrenError.value = false;

    try {
        const answer = getAnswer<{
            children?: Array<Record<string, unknown>>;
            activeChildId?: number;
        }>(await Settings.getChildren());

        if (!answer || !Array.isArray(answer.children)) {
            throw new Error(strings.errorChildren);
        }

        children.value = answer.children.map((item) => ({
            ...item,
            id: Number(item.id ?? item.childId),
            name: String(item.name ?? item.fullName ?? ""),
        }));

        const serverActiveId = Number(answer.activeChildId);

        if (Number.isFinite(serverActiveId) && serverActiveId > 0) {
            activeChildId.value = serverActiveId;
            settings.activeChildId = serverActiveId;
        }
    } catch (error) {
        Utilities.log(error);
        childrenError.value = true;
        Utilities.showText(strings.errorChildren);
    } finally {
        childrenLoading.value = false;
    }
}

async function selectChild(child: Child): Promise<void> {
    if (child.id === activeChildId.value || activeChildBusy.value) {
        return;
    }

    activeChildBusy.value = true;

    try {
        getAnswer(
            await Settings.setActiveChild(child.id),
        );

        activeChildId.value = child.id;
        settings.activeChildId = child.id;

        await Promise.all([
            loadMarksNotifications(),
            loadEaNotifications(),
        ]);
    } catch (error) {
        Utilities.log(error);
        Utilities.showText(strings.errorChildren);
    } finally {
        activeChildBusy.value = false;
    }
}

async function loadReview(): Promise<void> {
    reviewLoading.value = true;
    reviewError.value = false;

    try {
        const response = await Reviews.getMyReview();
        const answer = getAnswer<Record<string, unknown>>(response);

        const review = answer?.review;

        myReview.value = review && typeof review === "object"
            ? review as MyReview
            : null;
        myReviewOnModeration.value = answer.onModeration;
    } catch (error) {
        Utilities.log(error);
        reviewError.value = true;
        Utilities.showText(strings.errorReview);
    } finally {
        reviewLoading.value = false;
    }
}

function openReviewEditor(): void {
    editingReview.value = myReview.value !== null;
    showReviewEditor.value = true;
}

interface ReviewEditorResult {
    stars: number;
    text: string | null;
}

async function submitReview(
    review: ReviewEditorResult,
): Promise<void> {
    if (reviewActionBusy.value) {
        return;
    }

    reviewActionBusy.value = true;

    try {
        const response = await Reviews.createReview(
            review.stars,
            review.text,
        );

        getAnswer(response);

        showMessageDialog.value = true;
        messageDialogTitle.value = strings.titleDialogReviewSent;
        messageDialogText.value = strings.messageDialogReviewSent;

        await loadReview();
    } catch (error) {
        Utilities.log(error);
        Utilities.showText(strings.errorReview);
    } finally {
        reviewActionBusy.value = false;
    }
}

async function deleteMyReview(): Promise<void> {
    if (reviewActionBusy.value) {
        return;
    }

    reviewActionBusy.value = true;

    try {
        getAnswer(await Reviews.deleteReview());

        showDeleteReviewDialog.value = false;
        myReview.value = null;
        myReviewOnModeration.value = null;
    } catch (error) {
        Utilities.log(error);
        Utilities.showText(strings.errorReview);
    } finally {
        reviewActionBusy.value = false;
    }
}

function openAllReviews(): void {
    window.open(
        new URL("/#reviews", window.location.origin).toString(),
        "_blank",
        "noopener,noreferrer",
    );
}

async function loadReferral(): Promise<void> {
    referralLoading.value = true;
    referralError.value = false;

    try {
        referral.value = getAnswer<ReferralParams>(
            await Settings.getReferralParams(),
        );

        if (!referral.value) {
            throw new Error(strings.errorReferral);
        }
    } catch (error) {
        Utilities.log(error);
        referralError.value = true;
        Utilities.showText(strings.errorReferral);
    } finally {
        referralLoading.value = false;
    }
}

async function shareReferral(): Promise<void> {
    if (!referral.value) {
        return;
    }

    const url = referral.value.referralUrl;
    const text = strings.shareText(referral.value.referralUrl);

    try {
        if (navigator.share) {
            await navigator.share({ text, url });
            return;
        }

        await navigator.clipboard.writeText(text);

        showMessage(strings.share, strings.shareText);
    } catch (error) {
        Utilities.log(error);
        if (error instanceof Error && error.name === "AbortError") {
            return;
        }

        Utilities.showText(strings.errorReferral);
    }
}

function openSite(): void {
    window.open(
        new URL("/", window.location.origin).toString(),
        "_blank",
        "noopener,noreferrer",
    );
}

async function confirmLogout(): Promise<void> {
    showLogoutDialog.value = false;
    await logout();
}

onMounted(() => {
    void Promise.all([
        loadMarksNotifications(),
        loadEaNotifications(),
        loadChildren(),
        loadReview(),
        loadReferral(),
    ]);
});
</script>

<style scoped>
.settings-page {
    box-sizing: border-box;
    width: 100%;
    max-width: 720px;
    min-height: 100vh;
    min-height: 100dvh;
    margin-inline: auto;
    padding: 16px 16px calc(112px + env(safe-area-inset-bottom));
    overflow-y: auto;
    color: var(--text-primary);
}

.settings-card {
    min-width: 0;
    margin-bottom: 16px;
    padding: 16px;
    border: 1px solid var(--stroke-bg);
    border-radius: 18px;
    background: var(--bg-settings-block);
}

.section-title {
    margin: 0 0 12px;
    font-size: 18px;
    font-weight: 700;
}

.setting-row,
.setting-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.setting-row {
    min-height: 48px;
}

.setting-description {
    min-width: 0;
    line-height: 1.4;
}

.setting-value {
    flex-shrink: 0;
    color: var(--text-secondary);
    font-size: 13px;
}

.setting-heading {
    margin-bottom: 12px;
}

.setting-row-nested {
    padding-top: 4px;
}

.setting-error-button {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    padding: 0;
    border: 0;
    border-radius: 50%;
    background: transparent;
    color: #e53935;
    font-size: 26px;
    font-weight: 500;
    line-height: 1;
    cursor: pointer;
}

.setting-error-button:focus-visible {
    outline: 2px solid var(--slider-accent);
    outline-offset: 2px;
}

.setting-error-button:disabled {
    cursor: wait;
    opacity: 0.6;
}

.switch {
    position: relative;
    flex: 0 0 auto;
    width: 46px;
    height: 26px;
    margin: 0;
    appearance: none;
    border: 1px solid var(--stroke-bg);
    border-radius: 999px;
    background: var(--track-switch-simple);
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.switch::before {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--thumb-switch-simple);
    content: "";
    transition: transform 0.2s ease;
}

.switch:checked {
    background: var(--track-switch-checked);
}

.switch:checked::before {
    background: var(--thumb-switch-checked);
    transform: translateX(20px);
}

.switch:disabled {
    cursor: wait;
    opacity: 0.6;
}

.setting-range-block {
    margin-top: 14px;
}

.range-control,
.single-range-control {
    position: relative;
    min-height: 42px;
    padding: 10px 0;
    touch-action: pan-y;
}

.range-track {
    position: absolute;
    top: 50%;
    right: 0;
    left: 0;
    height: 4px;
    overflow: hidden;
    border-radius: 999px;
    background: var(--slider-track-off);
    transform: translateY(-50%);
    pointer-events: none;
}

.range-track-selected {
    position: absolute;
    top: 0;
    bottom: 0;
    border-radius: inherit;
    background: var(--slider-accent);
}

.range-input,
.single-range {
    position: absolute;
    top: 50%;
    left: 0;
    display: block;
    width: 100%;
    height: 32px;
    margin: 0;
    padding: 0;
    appearance: none;
    -webkit-appearance: none;
    background: transparent;
    transform: translateY(-50%);
    cursor: pointer;
    touch-action: pan-y;
}

.range-input {
    z-index: 2;
    pointer-events: none;
}

.range-input::-webkit-slider-thumb,
.single-range::-webkit-slider-thumb {
    pointer-events: auto;
}

.range-input::-moz-range-thumb,
.single-range::-moz-range-thumb {
    pointer-events: auto;
}

.range-input::-webkit-slider-runnable-track,
.single-range::-webkit-slider-runnable-track {
    height: 4px;
    background: transparent;
}

.range-input::-moz-range-track,
.single-range::-moz-range-track {
    height: 4px;
    background: transparent;
}

.range-input::-webkit-slider-thumb,
.single-range::-webkit-slider-thumb {
    width: 22px;
    height: 22px;
    margin-top: -9px;
    appearance: none;
    -webkit-appearance: none;
    border: 0;
    border-radius: 50%;
    background: var(--slider-accent);
    box-shadow: 0 1px 3px rgb(0 0 0 / 24%);
}

.range-input::-moz-range-thumb,
.single-range::-moz-range-thumb {
    width: 22px;
    height: 22px;
    border: 0;
    border-radius: 50%;
    background: var(--slider-accent);
    box-shadow: 0 1px 3px rgb(0 0 0 / 24%);
}

.range-input-left {
    z-index: 2;
}

.range-input-right {
    z-index: 3;
}

.slider-island {
    position: absolute;
    z-index: 5;
    bottom: calc(100% - 2px);
    min-width: max-content;
    max-width: 220px;
    padding: 6px 10px;
    border-radius: 8px;
    background: var(--slider-label-bg);
    color: var(--slider-label-text);
    font-size: 12px;
    line-height: 1.2;
    text-align: center;
    box-shadow: 0 2px 6px rgb(0 0 0 / 14%);
    transform: translateX(-50%);
    pointer-events: none;
}

.single-range {
    position: relative;
    z-index: 2;
    top: auto;
    height: 32px;
    transform: none;
    accent-color: var(--slider-accent);
}

.single-range-control .slider-island {
    bottom: calc(100% - 3px);
}

.single-range-control .range-track-selected {
    left: 0;
}

.range-control-active .range-track-selected {
    background: var(--slider-accent);
}

.setting-warning {
    margin: 10px 0 0;
    color: var(--settings-warning);
    font-weight: 600;
    font-size: 13px;
    line-height: 1.4;
}

.section-heading-button {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0;
    border: 0;
    background: transparent;
    color: inherit;
    text-align: left;
    cursor: pointer;
}

.section-heading-button .section-title {
    margin-bottom: 0;
}

.section-chevron {
    color: var(--text-secondary);
    font-size: 24px;
}

.child-option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    min-height: 46px;
    margin-top: 8px;
    padding: 12px;
    border: 1px solid var(--stroke-bg);
    border-radius: 12px;
    background: var(--button-bg);
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
}

.child-option:disabled {
    cursor: default;
    opacity: 0.75;
}

.child-option-active {
    cursor: default;
}

.child-active {
    color: var(--text-secondary);
    font-size: 12px;
}

.state-message {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 12px 0 0;
    color: var(--text-secondary);
    line-height: 1.4;
}

.text-button {
    padding: 4px 0;
    border: 0;
    background: transparent;
    color: var(--developer-text);
    font: inherit;
    cursor: pointer;
}

.action-button {
    display: block;
    width: 100%;
    min-height: 46px;
    margin-top: 10px;
    padding: 12px 16px;
    border: 1px solid var(--stroke-bg);
    border-radius: 12px;
    background: var(--button-bg);
    color: var(--text-primary);
    font: inherit;
    font-weight: 600;
    cursor: pointer;
}

.action-button:disabled {
    cursor: wait;
    opacity: 0.6;
}

.action-button-secondary {
    background: var(--button-bg);
}

.review-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
}

.review-star {
    color: var(--text-secondary);
    font-size: 32px;
}

.review-star-filled {
    color: var(--review-star-filled);
}

.review-status {
    color: var(--text-secondary);
}

.review-text {
    margin: 12px 0;
    line-height: 1.5;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}

.review-likes {
    color: var(--text-primary);
    font-size: 15px;
}

.review-editor {
    display: grid;
    gap: 10px;
    margin-top: 12px;
}

.review-editor-stars {
    display: flex;
    justify-content: center;
    gap: 8px;
}

.review-star-button {
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--text-secondary);
    font-size: 34px;
    cursor: pointer;
}

.review-input {
    box-sizing: border-box;
    width: 100%;
    min-height: 120px;
    padding: 12px;
    border: 1px solid var(--stroke-bg);
    border-radius: 12px;
    background: var(--bg-login-about);
    color: var(--text-primary);
    font: inherit;
    resize: vertical;
}

.review-counter {
    margin: 0;
    color: var(--text-secondary);
    font-size: 12px;
    text-align: right;
}

.about-description {
    margin: 0;
    line-height: 1.5;
    white-space: pre-line;
}

.about-meta p {
    margin: 6px 0;
    color: var(--text-secondary);
    font-size: 13px;
}

.loader {
    display: inline-block;
    width: 16px;
    height: 16px;
    flex: 0 0 auto;
    border: 2px solid var(--stroke-bg);
    border-top-color: var(--slider-accent);
    border-radius: 50%;
    animation: settings-loader 0.7s linear infinite;
}

@media (max-width: 480px) {
    .settings-page {
        padding-right: 16px;
        padding-left: 16px;
    }
}

@keyframes settings-loader {
    to {
        transform: rotate(360deg);
    }
}
</style>
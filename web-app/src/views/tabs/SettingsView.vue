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
                    v-if="eaNotificationsLoaded"
                    class="setting-row setting-row-nested"
                >
                    <span class="setting-description">
                        {{ strings.settingsEaNotifications }}
                    </span>

                    <input
                        v-model="eaNotifications"
                        class="switch"
                        type="checkbox"
                        :disabled="eaNotificationsBusy"
                        @change="toggleEaNotifications"
                    />
                </label>

                <button
                    v-if="eaNotificationsError"
                    class="text-button"
                    type="button"
                    @click="loadEaNotifications"
                >
                    {{ strings.errorEaNotifications }}
                </button>
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
                    v-if="marksNotificationsLoaded"
                    class="setting-row setting-row-nested"
                >
                    <span class="setting-description">
                        {{ strings.settingsMarksNotifications }}
                    </span>

                    <input
                        v-model="marksNotifications"
                        class="switch"
                        type="checkbox"
                        :disabled="marksNotificationsBusy"
                        @change="toggleMarksNotifications"
                    />
                </label>

                <button
                    v-if="marksNotificationsError"
                    class="text-button"
                    type="button"
                    @click="loadMarksNotifications"
                >
                    {{ strings.errorMarksNotifications }}
                </button>
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

            <div>
                <div class="setting-heading">
                    <span class="setting-description">
                        {{ strings.settingsSchedulePeriod }}
                    </span>

                    <span class="setting-value">
                        {{ scheduleRangeText }}
                    </span>
                </div>

                <div class="range-control">
                    <input
                        v-model.number="scheduleLeft"
                        type="range"
                        min="-14"
                        max="0"
                        step="1"
                        :aria-label="strings.scheduleRangeLabelFrom"
                        @input="updateScheduleRange('left')"
                        @change="saveScheduleRange"
                    />

                    <input
                        v-model.number="scheduleRight"
                        type="range"
                        min="1"
                        max="21"
                        step="1"
                        :aria-label="strings.scheduleRangeLabelTo"
                        @input="updateScheduleRange('right')"
                        @change="saveScheduleRange"
                    />
                </div>

                <div class="range-labels">
                    <span>{{ strings.scheduleRangeLabelFrom(beforeSchedule) }}</span>
                    <span>{{ strings.scheduleRangeLabelTo(afterSchedule) }}</span>
                    <span>{{ strings.lastMarksLabel(lastMarksPeriod) }}</span>
                </div>

                <p
                    v-if="scheduleWarning"
                    class="setting-warning"
                >
                    {{ strings.settingsScheduleWarning }}
                </p>
            </div>

            <div>
                <div class="setting-heading">
                    <span class="setting-description">
                        {{ strings.settingsLastMarksPeriod }}
                    </span>

                    <span class="setting-value">
                        {{ lastMarksPeriod }}
                    </span>
                </div>

                <input
                    v-model.number="lastMarksPeriod"
                    class="single-range"
                    type="range"
                    min="1"
                    max="14"
                    step="1"
                    :aria-label="strings.settingsLastMarksPeriod"
                    @change="saveLastMarksPeriod"
                />

                <p class="setting-value">
                    {{ strings.lastMarksLabel(lastMarksPeriod) }}
                </p>

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

                <span class="section-chevron">
                    {{ childrenExpanded ? "−" : "+" }}
                </span>
            </button>

            <p
                v-if="childrenLoading"
                class="state-message"
            >
                <span class="loader"></span>
            </p>

            <p
                v-else-if="childrenError"
                class="state-message"
            >
                {{ strings.errorChildren }}

                <button
                    class="text-button"
                    type="button"
                    @click="loadChildren"
                >
                    {{ strings.update }}
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
                    v-for="child in children"
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
                        {{ strings.loadActiveProfile }}
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

            <div
                v-else-if="reviewError"
                class="state-message"
            >
                {{ strings.errorReview }}

                <button
                    class="text-button"
                    type="button"
                    @click="loadReview"
                >
                    {{ strings.update }}
                </button>
            </div>

            <template v-else-if="myReview">
                <div class="review-meta">
                    <span
                        v-for="star in 5"
                        :key="star"
                        class="review-star"
                        :class="{ 'review-star-filled': star <= reviewStars }"
                    >
                        ★
                    </span>

                    <span class="review-status">
                        {{
                            strings.reviewMeta(
                                myReview.name,
                                myReview.createdAt,
                                (myReview.isUpdated ? strings.reviewEditMarker : '') +
                                    (myReview.onModeration ? strings.reviewModerationMarker : '')
                            )
                        }}
                    </span>
                </div>

                <p class="review-text">
                    {{ myReview.text }}
                </p>

                <p class="review-likes">
                    ♥ {{ myReview.likesCount ?? myReview.likes ?? 0 }}
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

            <div
                v-else-if="referralError"
                class="state-message"
            >
                {{ strings.errorReferral }}

                <button
                    class="text-button"
                    type="button"
                    @click="loadReferral"
                >
                    {{ strings.update }}
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
                            ? referral.isParent
                                ? strings.allActiveRelativesChildren
                                : strings.allActiveRelativesParents
                            : referral.isParent
                                ? strings.activeRelativesChildren(referral.countActiveRelatives, referral.countRelatives)
                                : strings.activeRelativesParents(referral.countActiveRelatives, referral.countRelatives)
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
            :cancel-text="strings.ok"
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
            :cancel-text="strings.ok"
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
    id?: number;
    stars?: number;
    rating?: number;
    text: string;
    moderated?: boolean;
    likesCount?: number;
    likes?: number;
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

const scheduleRangeText = computed(() => {
    const before = Math.abs(scheduleLeft.value);
    const after = scheduleRight.value;

    return `${before} / ${after}`;
});

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
    } catch {
        marksNotificationsError.value = true;
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
    } catch {
        marksNotifications.value = previous;
        showMessage(
            strings.errorMarksNotifications,
            strings.errorMarksNotifications,
        );
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
    } catch {
        eaNotificationsError.value = true;
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
    } catch {
        eaNotifications.value = previous;
        showMessage(
            strings.errorEaNotifications,
            strings.errorEaNotifications,
        );
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
    } catch {
        childrenError.value = true;
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
    } catch {
        showMessage(strings.errorChildren, strings.errorChildren);
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
    } catch {
        reviewError.value = true;
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
    } catch {
        showMessage(
            strings.errorCreateReview,
            strings.errorCreateReview,
        );
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
    } catch {
        showMessage(
            strings.errorDeleteReview,
            strings.errorDeleteReview,
        );
    } finally {
        reviewActionBusy.value = false;
    }
}

function openAllReviews(): void {
    window.open(
        new URL("/", window.location.origin).toString(),
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
    } catch {
        referralError.value = true;
    } finally {
        referralLoading.value = false;
    }
}

async function shareReferral(): Promise<void> {
    if (!referral.value) {
        return;
    }

    const url = referral.value.referralUrl;
    const text = strings.shareText(referralUrl);

    try {
        if (navigator.share) {
            await navigator.share({ text, url });
            return;
        }

        await navigator.clipboard.writeText(text);

        showMessage(strings.share, strings.shareText);
    } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
            return;
        }

        showMessage(strings.errorReferral, strings.errorReferral);
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
    min-height: 100vh;
    min-height: 100dvh;
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
    background: var(--dialog-background);
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

.switch {
    position: relative;
    flex: 0 0 auto;
    width: 46px;
    height: 26px;
    margin: 0;
    appearance: none;
    border: 1px solid var(--stroke-bg);
    border-radius: 999px;
    background: var(--bg-bottom-menu);
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
    background: var(--bottom-menu-icon-checked);
    content: "";
    transition: transform 0.2s ease;
}

.switch:checked {
    background: var(--slider-accent);
}

.switch:checked::before {
    transform: translateX(20px);
}

.switch:disabled {
    cursor: wait;
    opacity: 0.6;
}

.range-control {
    position: relative;
    display: grid;
    gap: 6px;
    padding: 8px 0;
}

.range-control input[type="range"],
.single-range {
    width: 100%;
    margin: 0;
    accent-color: var(--slider-accent);
}

.range-control input[type="range"] {
    grid-area: 1 / 1;
}

.range-labels {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 12px;
}

.setting-warning {
    margin: 10px 0 0;
    color: var(--developer-text);
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
    background: var(--bg-bottom-menu);
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
}

.child-option:disabled {
    cursor: default;
    opacity: 0.75;
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
    background: var(--bg-bottom-menu);
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
    background: transparent;
}

.review-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px;
}

.review-star {
    color: var(--text-secondary);
    font-size: 22px;
}

.review-star-filled {
    color: var(--slider-accent);
}

.review-status {
    margin-left: 8px;
    color: var(--text-secondary);
    font-size: 12px;
}

.review-text {
    margin: 12px 0;
    line-height: 1.5;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}

.review-likes {
    color: var(--text-secondary);
    font-size: 13px;
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
    background: var(--dialog-background);
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

@keyframes settings-loader {
    to {
        transform: rotate(360deg);
    }
}
</style>
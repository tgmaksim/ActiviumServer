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
                />
            </label>

            <div>
                <label class="setting-row setting-row-nested">
                    <span class="setting-description">
                        {{ strings.settingsEaNotifications }}
                    </span>

                    <span
                        v-if="settingsViewModel.statusEANotificationsState.value.type === 'loading'"
                        class="loader"
                        aria-label="Loading"
                    ></span>

                    <button
                        v-else-if="isLoadError(settingsViewModel.statusEANotificationsState.value)"
                        class="setting-error-button"
                        type="button"
                        :aria-label="strings.errorEaNotifications"
                        @click="settingsViewModel.loadEANotifications()"
                    >
                        ×
                    </button>

                    <input
                        v-else-if="settingsViewModel.statusEANotificationsState.value.type === 'success'"
                        :checked="settingsViewModel.statusEANotificationsState.value.data.status"
                        class="switch"
                        type="checkbox"
                        @change="toggleEaNotifications"
                    />
                </label>
            </div>

            <div>
                <label class="setting-row setting-row-nested">
                    <span class="setting-description">
                        {{ strings.settingsMarksNotifications }}
                    </span>

                    <span
                        v-if="settingsViewModel.statusMarksNotificationsState.value.type === 'loading'"
                        class="loader"
                        aria-label="Loading"
                    ></span>

                    <button
                        v-else-if="isLoadError(settingsViewModel.statusMarksNotificationsState.value)"
                        class="setting-error-button"
                        type="button"
                        :aria-label="strings.errorMarksNotifications"
                        @click="settingsViewModel.loadMarksNotifications()"
                    >
                        ×
                    </button>

                    <input
                        v-else-if="settingsViewModel.statusMarksNotificationsState.value.type === 'success'"
                        :checked="settingsViewModel.statusMarksNotificationsState.value.data.status"
                        class="switch"
                        type="checkbox"
                        @change="toggleMarksNotifications"
                    />
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
                        min="1"
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

        <section v-if="!pwaInstalled" class="settings-card">
            <h2 class="section-title">
                {{ strings.titleDialogPwaInstall }}
            </h2>

            <p class="about-description">
                {{ strings.pwaInstallAbout }}
            </p>

            <button
                class="action-button"
                type="button"
                @click="settings.showInstallDialog = true"
            >
                {{ strings.buttonDialogPwaInstall }}
            </button>
        </section>

        <section class="settings-card">
            <h2 class="section-title">
                {{ strings.activeProfile }}
            </h2>

            <button
                v-if="settingsViewModel.childrenState.value.type === 'success'"
                class="child-profile-trigger"
                type="button"
                :aria-expanded="childrenExpanded"
                @click="toggleChildren"
            >
                <span class="child-profile-trigger-text">
                    {{
                        childrenExpanded
                            ? strings.selectProfile
                            : activeChild?.name ?? strings.noChild
                    }}
                </span>

                <span
                    class="child-profile-chevron"
                    :class="{ 'child-profile-chevron-expanded': childrenExpanded }"
                    aria-hidden="true"
                >
                    ▾
                </span>
            </button>

            <div
                v-else
                class="child-profile-trigger child-profile-trigger-static"
                aria-live="polite"
            >
                <span class="child-profile-trigger-text">
                    {{ strings.loadActiveProfile }}
                </span>

                <span
                    v-if="settingsViewModel.childrenState.value.type === 'loading'"
                    class="loader"
                    role="status"
                    :aria-label="strings.loadActiveProfile"
                ></span>

                <button
                    v-else-if="isLoadError(settingsViewModel.childrenState.value)"
                    class="setting-error-button"
                    type="button"
                    :aria-label="strings.errorChildren"
                    @click.stop="retryChildren"
                >
                    ×
                </button>
            </div>

            <!-- Список доступных профилей -->
            <div
                v-if="childrenExpanded && settingsViewModel.childrenState.value.type === 'success'"
                class="children-list"
            >
                <p
                    v-if="children.length === 0"
                    class="state-message"
                >
                    {{ strings.noChild }}
                </p>

                <button
                    v-for="child in children"
                    :key="child.childId"
                    class="child-option"
                    :class="{
                        'child-option-active': child.childId === settings.activeChildId,
                    }"
                    type="button"
                    :aria-current="
                        child.childId === settings.activeChildId ? 'true' : undefined
                    "
                    @click="selectChild(child.childId)"
                >
                    <span>{{ child.name }}</span>

                    <span
                        v-if="child.childId === settings.activeChildId"
                        class="child-active"
                    >
                        {{ strings.selectedProfile }}
                    </span>
                </button>
            </div>
        </section>

        <section class="settings-card">
            <div class="review-header">
                <h2 class="section-title">
                    {{ strings.review }}
                </h2>

                <span
                    v-if="settingsViewModel.reviewState.value.type == 'loading'"
                    class="review-header-action"
                    role="status"
                    :aria-label="strings.review"
                >
                    <span class="loader"></span>
                </span>

                <button
                    v-else-if="isLoadError(settingsViewModel.reviewState.value)"
                    class="setting-error-button review-header-action"
                    type="button"
                    :aria-label="strings.errorReview"
                    @click="settingsViewModel.loadReview()"
                >
                    ×
                </button>

                <button
                    v-else-if="settingsViewModel.reviewState.value.type == 'success'"
                    class="review-refresh-button review-header-action"
                    type="button"
                    :aria-label="strings.review"
                    @click="settingsViewModel.loadReview()"
                >
                    <img
                        src="@/assets/ic_refresh.svg"
                        alt=""
                        aria-hidden="true"
                    />
                </button>
            </div>

            <template v-if="myReview">
                <span class="review-status">
                    {{
                        strings.reviewMeta(
                            myReview.name,
                            new Intl.DateTimeFormat("ru-RU", {
                                day: "2-digit",
                                month: "2-digit",
                                year: "numeric",
                            }).format(new Date(myReview.createdAt)),
                            (myReview.isUpdated ? strings.reviewEditMarker : "") +
                                (myReviewOnModeration
                                    ? strings.reviewModerationMarker
                                    : ""),
                        )
                    }}
                </span>

                <div
                    class="review-meta"
                    :aria-label="`${reviewStars} из 5`"
                >
                    <span
                        v-for="star in 5"
                        :key="star"
                        class="review-star"
                        :class="{ 'review-star-filled': star <= reviewStars }"
                        aria-hidden="true"
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
                    class="action-button"
                    type="button"
                    @click="showDeleteReviewDialog = true"
                >
                    {{ strings.deleteReview }}
                </button>
            </template>

            <button
                v-else-if="settingsViewModel.reviewState.value.type === 'success'"
                class="action-button"
                type="button"
                @click="openReviewEditor"
            >
                {{ strings.writeReview }}
            </button>

            <button
                class="action-button"
                type="button"
                @click="openAllReviews"
            >
                {{ strings.openAllReviews }}
            </button>
        </section>

        <section class="settings-card">
            <div class="referral-header">
                <h2 class="section-title">
                    {{ strings.referral }}
                </h2>

                <span
                    v-if="settingsViewModel.referralState.value.type === 'loading'"
                    class="referral-header-action"
                    role="status"
                    :aria-label="strings.referral"
                >
                    <span class="loader"></span>
                </span>

                <button
                    v-else-if="isLoadError(settingsViewModel.referralState.value)"
                    class="setting-error-button referral-header-action"
                    type="button"
                    :aria-label="strings.errorReferral"
                    @click="settingsViewModel.loadReferralParams()"
                >
                    ×
                </button>
            </div>

            <template v-if="settingsViewModel.referralState.value.type === 'success'">
                <p v-if="settingsViewModel.referralState.value.data.meReferralName">
                    {{ strings.meReferral(settingsViewModel.referralState.value.data.meReferralName) }}
                </p>

                <p>
                    {{ strings.referralCount(settingsViewModel.referralState.value.data.referralsCount) }}
                </p>

                <p>
                    {{
                        settingsViewModel.referralState.value.data.countActiveRelatives === settingsViewModel.referralState.value.data.countRelatives
                            ? (
                                settingsViewModel.referralState.value.data.isParent
                                    ? strings.allActiveRelativesChildren
                                    : strings.allActiveRelativesParents
                            )
                            : (
                                settingsViewModel.referralState.value.data.isParent
                                    ? strings.activeRelativesChildren(
                                        settingsViewModel.referralState.value.data.countActiveRelatives,
                                        settingsViewModel.referralState.value.data.countRelatives,
                                    )
                                    : strings.activeRelativesParents(
                                        settingsViewModel.referralState.value.data.countActiveRelatives,
                                        settingsViewModel.referralState.value.data.countRelatives,
                                    )
                            )
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
            :loading="settingsViewModel.reviewState.value.type == 'loading'"
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
    ref,
    watch,
} from "vue";

import AppDialog from "@/components/AppDialog.vue";
import { strings } from "@/constants/strings";
import { NotificationPermission } from "@/notifications/permission";
import { useSettingsStore } from "@/stores/settings";
import { logout } from "@/utils/logout";
import { Utilities } from "@/utils/utils";
import { SettingsViewModel } from "./settings-view-model";
import { setShownError, setLoading, isLoadError } from "@/ui-core/state-utils";
import ReviewEditorDialog from "./ReviewEditorDialog.vue";

import { getDeviceInfo } from "@/utils/device";
import { APP_VERSION, APP_VERSION_CODE } from "@/constants/app";
import { pwaInstalled } from "@/utils/pwa-install";

const settingsViewModel = new SettingsViewModel();
const settings = useSettingsStore();
const deviceInfo = getDeviceInfo();

const scheduleLeft = ref(-settings.beforeSchedule);
const scheduleRight = ref(settings.afterSchedule);
const lastMarksPeriod = ref(settings.lastMarksPeriod);

const activeScheduleThumb = ref<"left" | "right" | null>(null);
const lastMarksSliderActive = ref(false);

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

const childrenExpanded = ref(false);

const children = computed(
    () => settingsViewModel.childrenState.value.data?.children ?? [],
);

const activeChild = computed(
    () =>
        children.value.find(
            (child) => child.childId === settings.activeChildId,
        ) ?? null,
);

const myReview = computed(
    () => settingsViewModel.reviewState.value.data?.review ?? null,
);

const myReviewOnModeration = computed(
    () => settingsViewModel.reviewState.value.data?.onModeration ?? false,
);

const reviewStars = computed(
    () => Number(myReview.value?.stars ?? 0),
);

const showReviewEditor = ref(false);
const editingReview = ref(false);

const showDeleteReviewDialog = ref(false);
const showLogoutDialog = ref(false);

const showMessageDialog = ref(false);
const messageDialogTitle = ref("");
const messageDialogText = ref("");

watch(
    () => settingsViewModel.statusEANotificationsState.value,
    (state) => {
        if (state.type === "empty") {
            settingsViewModel.loadEANotifications();
            return;
        }

        if (state.type === "error") {
            Utilities.showUiMessage(state.message);

            settingsViewModel.statusEANotificationsState.value =
                setShownError(state);
        }
    },
    { immediate: true },
);

watch(
    () => settingsViewModel.statusMarksNotificationsState.value,
    (state) => {
        if (state.type === "empty") {
            settingsViewModel.loadMarksNotifications();
            return;
        }

        if (state.type === "error") {
            Utilities.showUiMessage(state.message);

            settingsViewModel.statusMarksNotificationsState.value =
                setShownError(state);
        }
    },
    { immediate: true },
);

watch(
    () => settingsViewModel.childrenState.value,
    (state) => {
        if (state.type === "empty") {
            settingsViewModel.loadChildren();
            return;
        }

        if (state.type === "error") {
            Utilities.showUiMessage(state.message);

            settingsViewModel.childrenState.value = setShownError(state);
        }
    },
    { immediate: true },
);

watch(
    () => settingsViewModel.reviewState.value,
    (state) => {
        switch (state.type) {
            case "empty":
                settingsViewModel.loadReview();
                break;

            case "loading":
            case "shownError":
                break;

            case "error":
                Utilities.showUiMessage(state.message);

                settingsViewModel.reviewState.value = setShownError(state);
                break;

            case "success":
                // Отправка отзыва завершилась успешно.
                if (showReviewEditor.value) {
                    showReviewEditor.value = false;

                    showMessageDialog.value = true;
                    messageDialogTitle.value = strings.titleDialogReviewSent;
                    messageDialogText.value = strings.messageDialogReviewSent;
                }

                // Удаление отзыва завершилось успешно.
                if (showDeleteReviewDialog.value) {
                    showDeleteReviewDialog.value = false;
                }

                break;
        }
    },
    { immediate: true },
);

watch(
    () => settingsViewModel.referralState.value,
    (state) => {
        if (state.type === "empty") {
            settingsViewModel.loadReferralParams();
            return;
        }

        if (state.type === "error") {
            Utilities.showUiMessage(state.message);

            settingsViewModel.referralState.value = setShownError(state);
        }
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

async function toggleMarksNotifications(event: Event): Promise<void> {
    const desired = (event.target as HTMLInputElement).checked;

    const previousState = settingsViewModel.statusMarksNotificationsState.value;
    settingsViewModel.statusMarksNotificationsState.value =
        setLoading(settingsViewModel.statusMarksNotificationsState);

    if (desired) {
        try {
            const permission = await NotificationPermission.checkPermission();

            if (permission !== "granted") {
                const result = await NotificationPermission.enableNotifications();

                if (result !== "enabled") {
                    settingsViewModel.statusMarksNotificationsState.value = previousState;
                    return;
                }
            }
        } catch (error: unknown) {
            settingsViewModel.statusMarksNotificationsState.value = previousState;
            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Ошибка при проверке уведомлений"
            );
        }
    }

    settingsViewModel.switchMarksNotifications(desired);
}

async function toggleEaNotifications(event: Event): Promise<void> {
    const desired = (event.target as HTMLInputElement).checked;

    const previousState = settingsViewModel.statusEANotificationsState.value;
    settingsViewModel.statusEANotificationsState.value =
        setLoading(settingsViewModel.statusEANotificationsState);

    if (desired) {
        try {
            const permission = await NotificationPermission.checkPermission();

            if (permission !== "granted") {
                const result = await NotificationPermission.enableNotifications();

                if (result !== "enabled") {
                    settingsViewModel.statusMarksNotificationsState.value = previousState;
                    return;
                }
            }
        } catch (error: unknown) {
            settingsViewModel.statusMarksNotificationsState.value = previousState;
            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Ошибка при проверке уведомлений"
            );
        }
    }

    settingsViewModel.switchEANotifications(desired);
}

function toggleChildren(): void {
    if (settingsViewModel.childrenState.value.type !== "success") {
        return;
    }

    childrenExpanded.value = !childrenExpanded.value;
}

function retryChildren(): void {
    childrenExpanded.value = false;
    settingsViewModel.loadChildren();
}

function selectChild(childId: number): void {
    childrenExpanded.value = false;

    // ViewModel самостоятельно обработает совпадение ID,
    // выполнит запрос и обновит настройки уведомлений.
    settingsViewModel.setActiveChild(childId);
}

function openReviewEditor(): void {
    editingReview.value = myReview.value !== null;
    showReviewEditor.value = true;
}

interface ReviewEditorResult {
    stars: number;
    text: string | null;
}

function submitReview(review: ReviewEditorResult): void {
    if (settingsViewModel.reviewState.value.type === "loading") {
        return;
    }

    settingsViewModel.sendReview(review.stars, review.text);
}

function deleteMyReview(): void {
    if (settingsViewModel.reviewState.value.type === "loading") {
        return;
    }

    settingsViewModel.deleteReview();
}

function openAllReviews(): void {
    window.open(
        new URL("/#reviews", window.location.origin).toString(),
        "_blank",
        "noopener,noreferrer",
    );
}

async function shareReferral(): Promise<void> {
    const referral = settingsViewModel.referralState.value.type === "success"
        ? settingsViewModel.referralState.value.data
        : null;

    if (!referral) {
        return;
    }

    const url = referral.referralUrl;
    const text = strings.shareText(url);

    try {
        if (navigator.share) {
            await navigator.share({ text, url });
            return;
        }

        await navigator.clipboard.writeText(text);

        Utilities.showText(strings.textCopied);
    } catch (error: unknown) {
        Utilities.log(
            error instanceof Error
                ? error
                : new Error(String(error)),
            "Ошибка при попытке поделиться ссылкой"
        );

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
</script>

<style scoped>
.settings-page {
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    max-width: 720px;
    min-height: 0;
    margin-inline: auto;
    padding: 16px 16px calc(112px + env(safe-area-inset-bottom));
    overflow-x: hidden;
    overflow-y: auto;
    color: var(--text-primary);
    scrollbar-width: none;
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

.child-profile-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    min-height: 46px;
    margin-top: 12px;
    padding: 12px;
    border: 1px solid var(--stroke-bg);
    border-radius: 12px;
    background: var(--button-bg);
    color: inherit;
    font: inherit;
    text-align: left;
}

button.child-profile-trigger {
    cursor: pointer;
}

.child-profile-trigger-static {
    cursor: default;
}

.child-profile-trigger-text {
    min-width: 0;
    overflow-wrap: anywhere;
}

.child-profile-chevron {
    display: inline-flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    font-size: 20px;
    line-height: 1;
    transform: rotate(0deg);
    transition: transform 200ms ease;
}

.child-profile-chevron-expanded {
    transform: rotate(180deg);
}

.children-list {
    display: flex;
    flex-direction: column;
    min-width: 0;
    margin-top: 8px;
}

.child-option:focus-visible,
.child-profile-trigger:focus-visible {
    outline: 2px solid var(--slider-accent);
    outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
    .child-profile-chevron {
        transition: none;
    }
}

.state-message {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 12px 0 0;
    color: var(--text-secondary);
    line-height: 1.4;
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

.review-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-height: 32px;
    margin-bottom: 12px;
}

.review-header .section-title {
    min-width: 0;
    margin: 0;
}

.review-header-action {
    display: inline-flex;
    flex: 0 0 32px;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    margin-left: auto;
}

.review-refresh-button {
    padding: 6px;
    border: 0;
    border-radius: 50%;
    background: transparent;
    cursor: pointer;
}

.review-refresh-button img {
    display: block;
    width: 20px;
    height: 20px;
}

.review-refresh-button:focus-visible {
    outline: 2px solid var(--slider-accent);
    outline-offset: 2px;
}

.review-refresh-button:disabled {
    cursor: wait;
    opacity: 0.6;
}

.referral-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-height: 32px;
    margin-bottom: 12px;
}

.referral-header .section-title {
    min-width: 0;
    margin: 0;
}

.referral-header-action {
    display: inline-flex;
    flex: 0 0 32px;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    margin-left: auto;
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
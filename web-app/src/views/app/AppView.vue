<template>
    <div class="app-layout">
        <main class="app-content">
            <RouterView v-slot="{ Component }">
                <KeepAlive>
                    <component
                        :is="Component"
                        :settings-view-model="settingsViewModel"
                    />
                </KeepAlive>
            </RouterView>
        </main>

        <ConfettiCanvas />

        <Toast />

        <AppDialog
            :visible="currentInfo !== null"
            :title="currentInfo?.title ?? ''"
            :message="currentInfo?.text ?? ''"
            :action-text="strings.ok"
            @action="showNextInfo"
        />

        <footer class="app-footer">
            <BottomNavigation />
        </footer>
    </div>
</template>

<script setup lang="ts">
import {
    computed,
    onBeforeUnmount,
    onMounted,
    provide,
    ref,
    watch,
} from "vue";
import { useRoute, useRouter } from "vue-router";

import BottomNavigation from "@/components/BottomNavigation.vue";
import Toast from "@/components/Toast.vue";
import ConfettiCanvas from "@/components/ConfettiCanvas.vue";
import AppDialog from "@/components/AppDialog.vue";

import { AppViewModel, appViewModelKey } from "@/views/app/app-view-model";

import { SettingsViewModel } from "../tabs/settings/settings-view-model";

import { useConfetti } from "@/composables/useConfetti";
const {
    startConfettiAnimation,
} = useConfetti();

import { useSettingsStore } from "@/stores/settings";

import { LoadState } from "@/ui-core/load-state";
import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";

// Единый экземпляр ViewModel для всего приложения.
const appViewModel = new AppViewModel();
const settingsViewModel = new SettingsViewModel();

const settings = useSettingsStore();

provide(appViewModelKey, appViewModel);

const route = useRoute();
const router = useRouter();

type NotificationPageAction =
    | "update"
    | "today"
    | "update_review";

interface NotificationActionMessage {
    type: "notification-action";
    action: string;
    data: Record<string, unknown>;
}

interface NotificationData {
    profile?: string | number;
    notificationId?: number;
    from_notification?: string;
    good_mark?: string | boolean;
}

// Очередь информационных оповещений.
const infoMessages = ref<
    Array<{ title: string; text: string }>
>([]);

const infoIndex = ref(0);

// Текущее информационное оповещение.
const currentInfo = computed(
    () => infoMessages.value[infoIndex.value] ?? null,
);

// Отслеживание получения информационных оповещений.
watch(
    () => appViewModel.infoState.value,
    (state) => {
        // Обрабатываем только успешный ответ.
        if (!("data" in state)) {
            return;
        }

        infoMessages.value = state.data.messages.map(
            ({ title, text }) => ({
                title,
                text,
            }),
        );

        infoIndex.value = 0;

        // Если сообщений нет, сразу сбрасываем состояние.
        if (infoMessages.value.length === 0) {
            appViewModel.infoState.value = LoadState.empty();
        }
    },
);

/**
 * Показывает следующее информационное оповещение.
 */
function showNextInfo(): void {
    if (infoIndex.value + 1 < infoMessages.value.length) {
        infoIndex.value++;

        return;
    }

    // Все оповещения показаны.
    infoMessages.value = [];
    infoIndex.value = 0;

    appViewModel.infoState.value = LoadState.empty();
}

// Отслеживание возвращения приложения из фонового режима.
let wasHidden = false;

/**
 * Обрабатывает изменение видимости приложения.
 */
function handleVisibilityChange(): void {
    if (document.visibilityState === "hidden") {
        wasHidden = true;

        appViewModel.pauseStudy();

        return;
    }

    if (wasHidden) {
        wasHidden = false;

        appViewModel.checkAccessibleAd();
        appViewModel.checkStudy(() => route.name);
    }
}

async function receiveNotificationAction(
    action: string,
    data: NotificationData,
): Promise<void> {
    // Переключение профиля
    if (data.profile != null) {
        const profileId = Number(data.profile);

        if (Number.isFinite(profileId)) {
            settingsViewModel.setActiveChild(profileId, (result) => {
                const child = result.children.find(item => item.childId == result.activeChildId)

                if (child) {
                    Utilities.showText(strings.changeActiveChild(child.name), true);
                }
            });
        }
    }

    const notification = data.from_notification;

    let target:
        | {
            name: string;
            action: NotificationPageAction;
        }
        | null = null;
    let confetti: boolean = false;

    switch (notification) {
        case "new_mark":
            target = {
                name: "marks",
                action: "update",
            };
            confetti = data.good_mark ?? false;
            break;

        case "ea":
        case "remind_note":
            target = {
                name: "schedule",
                action: "today",
            };
            break;

        case "publish_review":
            target = {
                name: "settings",
                action: "update_review",
            };
            break;

        case "praise":
            confetti = true;
            break;
    }

    if (target) {
        await router.push({
            name: target.name,
            query: {
                ...route.query,
                notificationPageAction: target.action,
            },
        });
    }

    if (confetti) {
        startConfettiAnimation();
    }
}

function handleServiceWorkerMessage(event: MessageEvent): void {
    const message = event.data as NotificationActionMessage;

    if (message?.type !== "notification-action") {
        return;
    }

    void receiveNotificationAction(
        message.action,
        message.data,
    );
}

async function handleOpenWithAction() {
    // Обработка параметров, переданных через URL.
    const action = route.query.notificationAction;
    const rawData = route.query.notificationData;

    if (typeof action === "string") {
        let data: Record<string, unknown> = {};

        try {
            if (typeof rawData === "string") {
                const parsed: unknown = JSON.parse(rawData);

                if (
                    parsed !== null &&
                    typeof parsed === "object" &&
                    !Array.isArray(parsed)
                ) {
                    data = parsed as Record<string, unknown>;
                }
            }
        } catch (error) {
            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Failed to parse notification data:",
            );
        }

        // Удаляем параметры, чтобы действие не выполнилось повторно
        // при обновлении страницы.
        await router.replace({
            query: {
                ...route.query,
                notificationAction: undefined,
                notificationData: undefined,
            },
        });

        await receiveNotificationAction(action, data);
    }
}

onMounted(() => {
    document.addEventListener(
        "visibilitychange",
        handleVisibilityChange,
    );

    navigator.serviceWorker.addEventListener(
        "message",
        handleServiceWorkerMessage,
    );

    handleOpenWithAction();

    // Первоначальная проверка рекламы.
    appViewModel.checkAccessibleAd();

    // Первоначальная проверка информационных оповещений.
    appViewModel.checkInfoNotifications();

    // Первоначальная проверка обучающих подсказок.
    appViewModel.checkStudy(() => route.name);
});

onBeforeUnmount(() => {
    document.removeEventListener(
        "visibilitychange",
        handleVisibilityChange,
    );

    navigator.serviceWorker.removeEventListener(
        "message",
        handleServiceWorkerMessage,
    );

    appViewModel.pauseStudy();
});
</script>

<style scoped>
.app-layout {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    background: var(--main-bg);

    margin-top: env(safe-area-inset-top, 0);
}

.app-content {
    flex: 1 1 0;
    width: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
}

.app-footer {
    position: fixed;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 1000;

    display: flex;
    justify-content: center;

    width: 100%;
    box-sizing: border-box;
    padding: 8px 12px max(8px, env(safe-area-inset-bottom));

    pointer-events: none;
}

.app-footer :deep(.bottom-navigation) {
    width: 100%;
    max-width: 480px;
    pointer-events: auto;
}
</style>
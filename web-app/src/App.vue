<template>
    <RouterView />

    <AppDialog
        :visible="settings.showInstallDialog"
        :title="strings.titleDialogPwaInstall"
        :message="dialogMessage"
        :action-text="dialogActionText"
        :cancel-text="strings.buttonDialogPwaInstallCancel"
        @action="handleInstallAction"
        @cancel="dismissInstallDialog"
    />

    <AppDialog
        :visible="showNotificationDialog"
        :title="strings.titleDialogPermissionNotifications"
        :message="notificationDialogMessage"
        :action-text="notificationActionText"
        :cancel-text="
            notificationPermissionBlocked
                ? undefined
                : strings.buttonDialogPermissionNotificationsCancel
        "
        :loading="isEnablingNotifications"
        @action="handleNotificationAction"
        @cancel="showNotificationDialog = false"
    />
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, RouterView } from "vue-router";

import AppDialog from "@/components/AppDialog.vue";
import { strings } from "@/constants/strings";
import { Utilities } from "@/utils/utils";
import { routes } from "@/constants/routes"
import { NotificationPermission } from "@/notifications/permission";

import { useSettingsStore } from "@/stores/settings";

import {
    getPwaPlatform,
    shouldShowInstallPrompt,
    promptPwaInstall,
    hideInstallPrompt,
} from "@/utils/pwa-install";

const settings = useSettingsStore();
settings.showInstallDialog = false;
const showManualInstructions = ref(false);

const showNotificationDialog = ref(false);
const notificationPermissionBlocked = ref(false);
const isEnablingNotifications = ref(false);

const notificationDialogMessage = computed(() => {
    if (isEnablingNotifications.value) {
        return strings.messageDialogNotificationsConnecting;
    }

    return notificationPermissionBlocked.value
        ? strings.messageDialogPermissionNotificationsBlocked
        : strings.messageDialogPermissionNotifications;
});

const notificationActionText = computed(() => {
    if (isEnablingNotifications.value) {
        return strings.buttonDialogNotificationsConnecting;
    }

    return notificationPermissionBlocked.value
        ? strings.buttonDialogPermissionNotificationsManual
        : strings.buttonDialogPermissionNotifications;
});

const route = useRoute();

let checksStarted = false;

watch(
    () => route.path,
    (path) => {
        if (path === routes.loginBase) {
            checksStarted = false;
            settings.showInstallDialog = false;
            showNotificationDialog.value = false;
            return;
        }

        if (path !== routes.homeBase || checksStarted) {
            return;
        }

        checksStarted = true;

        if (shouldShowInstallPrompt()) {
            settings.showInstallDialog = true;
        } else {
            void checkNotifications();
        }
    },
    { immediate: true },
);

const platform = getPwaPlatform();

const dialogMessage = computed(() => {
    if (!showManualInstructions.value) {
        return strings.messageDialogPwaInstallIntro;
    }

    switch (platform) {
        case "android":
            return strings.messageDialogPwaInstallAndroid;

        case "ios":
            return strings.messageDialogPwaInstallIos;

        default:
            return strings.messageDialogPwaInstallOther;
    }
});

const dialogActionText = computed(() =>
    showManualInstructions.value
        ? strings.buttonDialogPwaInstallManual
        : strings.buttonDialogPwaInstall,
);

async function handleInstallAction(): Promise<void> {
    if (showManualInstructions.value) {
        finishInstallFlow();
        return;
    }

    const outcome = await promptPwaInstall();

    if (outcome === "accepted") {
        finishInstallFlow();
        return;
    }

    if (outcome === "unavailable") {
        showManualInstructions.value = true;
    }
}

function dismissInstallDialog(): void {
    hideInstallPrompt();
    finishInstallFlow();
}

async function checkNotifications(): Promise<void> {
    const state = await NotificationPermission.checkPermission();

    switch (state) {
        case "denied":
            notificationPermissionBlocked.value = true;
            showNotificationDialog.value = true;
            break;

        case "default":
            notificationPermissionBlocked.value = false;
            showNotificationDialog.value = true;
            break;

        case "unsupported":
        case "granted":
        case "error":
            break;
    }
}

function finishInstallFlow(): void {
    settings.showInstallDialog = false;
    void checkNotifications();
}

async function handleNotificationAction(): Promise<void> {
    if (notificationPermissionBlocked.value || isEnablingNotifications.value) {
        showNotificationDialog.value = false;
        return;
    }

    isEnablingNotifications.value = true;

    try {
        const result = await NotificationPermission.enableNotifications();

        switch (result) {
            case "enabled":
            case "unavailable":
                showNotificationDialog.value = false;
                break;

            case "denied":
                notificationPermissionBlocked.value = true;
                break;

            case "error":
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Не удалось включить уведомления",
                );
                showNotificationDialog.value = false;
                break;
        }
    } finally {
        isEnablingNotifications.value = false;
    }
}
</script>
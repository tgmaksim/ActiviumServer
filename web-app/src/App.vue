<template>
    <RouterView />

    <AppDialog
        :visible="showInstallDialog"
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
import { Messaging } from "@/firebase/messaging";
import { Settings } from "@/api/settings";
import { Utilities } from "@/utils/utils";
import { routes } from "@/constants/routes"

import {
    getPwaPlatform,
    shouldShowInstallPrompt,
    promptPwaInstall,
    hideInstallPrompt,
} from "@/utils/pwa-install";

const showInstallDialog = ref(false);
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
            showInstallDialog.value = false;
            showNotificationDialog.value = false;
            return;
        }

        if (path !== routes.homeBase || checksStarted) {
            return;
        }

        checksStarted = true;

        if (shouldShowInstallPrompt()) {
            showInstallDialog.value = true;
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

async function syncFirebaseToken(): Promise<void> {
    try {
        const token = await Messaging.getFcmToken();

        if (token === null) {
            return;
        }

        await Settings.updateFirebase(token);
    } catch (error) {
        Utilities.log(
            error,
            "Не удалось синхронизировать Firebase-токен",
        );
    }
}

async function checkNotifications(): Promise<void> {
    if (!("Notification" in window)) {
        return;
    }

    try {
        if (!await Messaging.isMessagingSupported()) {
            return;
        }

        switch (Notification.permission) {
            case "granted":
                await syncFirebaseToken();
                return;

            case "denied":
                notificationPermissionBlocked.value = true;
                showNotificationDialog.value = true;
                return;

            case "default":
                notificationPermissionBlocked.value = false;
                showNotificationDialog.value = true;
                return;
        }
    } catch (error) {
        Utilities.log(
            error,
            "Не удалось проверить поддержку уведомлений",
        );
    }
}

function finishInstallFlow(): void {
    showInstallDialog.value = false;
    void checkNotifications();
}

async function handleNotificationAction(): Promise<void> {
    if (notificationPermissionBlocked.value) {
        showNotificationDialog.value = false;
        return;
    }

    if (isEnablingNotifications.value) {
        return;
    }

    isEnablingNotifications.value = true;

    try {
        const token = await Messaging.enableNotifications();

        if (token !== null) {
            await Settings.updateFirebase(token);
            showNotificationDialog.value = false;
            return;
        }

        if (
            "Notification" in window &&
            Notification.permission === "denied"
        ) {
            notificationPermissionBlocked.value = true;
            return;
        }

        showNotificationDialog.value = false;
    } catch (error) {
        Utilities.log(
            error,
            "Не удалось включить уведомления",
        );
        showNotificationDialog.value = false;
    } finally {
        isEnablingNotifications.value = false;
    }
}
</script>
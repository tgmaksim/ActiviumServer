import { Settings } from "@/api/settings";
import { Messaging } from "@/firebase/messaging";
import { Utilities } from "@/utils/utils";
import { useSettingsStore } from "@/stores/settings";

export type NotificationPermissionState =
    | "unsupported"
    | "granted"
    | "denied"
    | "default"
    | "error";

export type EnableNotificationsResult =
    | "enabled"
    | "denied"
    | "unavailable"
    | "error";

/**
 * Проверка поддержки уведомлений и текущего разрешения браузера.
 *
 * Если разрешение уже выдано, синхронизирует Firebase-токен с сервером.
 */
async function checkPermission(): Promise<NotificationPermissionState> {
    if (
        typeof window === "undefined" ||
        !("Notification" in window)
    ) {
        return "unsupported";
    }

    try {
        if (!await Messaging.isMessagingSupported()) {
            return "unsupported";
        }

        switch (Notification.permission) {
            case "granted":
                await syncFirebaseToken();
                return "granted";

            case "denied":
                return "denied";

            case "default":
                return "default";

            default:
                return "error";
        }
    } catch (error) {
        Utilities.log(
            error instanceof Error
                ? error
                : new Error(String(error)),
            "Не удалось проверить поддержку уведомлений",
        );

        return "error";
    }
}

/**
 * Запрашивает разрешение браузера и регистрирует Firebase-токен на сервере.
 */
async function enableNotifications(): Promise<EnableNotificationsResult> {
    try {
        const token = await Messaging.enableNotifications();

        if (token === null) {
            if (
                "Notification" in window &&
                Notification.permission === "denied"
            ) {
                return "denied";
            }

            return "unavailable";
        }

        await saveFirebaseToken(token);

        return "enabled";
    } catch (error) {
        Utilities.log(
            error instanceof Error
                ? error
                : new Error(String(error)),
            "Не удалось включить уведомления",
        );

        return "error";
    }
}

/**
 * Получает текущий Firebase-токен и синхронизирует его с сервером.
 */
async function syncFirebaseToken(): Promise<void> {
    const token = await Messaging.getFcmToken();

    if (token === null) {
        return;
    }

    await saveFirebaseToken(token);
}

/**
 * Сохраняет токен на сервере и обновляет локальное состояние.
 */
async function saveFirebaseToken(token: string): Promise<void> {
    const response = await Settings.updateFirebase(token);

    if (!response.status) {
        throw new Error(
            response.error?.errorMessage ??
                "Не удалось зарегистрировать уведомления",
        );
    }

    useSettingsStore().firebaseMessagingToken = token;
}

export const NotificationPermission = {
    checkPermission,
    enableNotifications,
};
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

let unsubscribeRegistration: (() => void) | undefined;

let registrationPromise: Promise<void> | null = null;

function syncRegistrationInBackground(): void {
    if (registrationPromise !== null) {
        return;
    }

    registrationPromise = (async () => {
        await ensureRegistrationListener();
        await Messaging.registerForNotifications();
    })()
        .catch((error) => {
            Utilities.log(
                error instanceof Error
                    ? error
                    : new Error(String(error)),
                "Не удалось синхронизировать регистрацию Firebase",
            );
        })
        .finally(() => {
            registrationPromise = null;
        });
}

/**
 * Синхронизация Firebase Installation ID с сервером.
 */
async function saveFirebaseInstallationId(fid: string): Promise<void> {
    const response = await Settings.updateFirebase(fid);

    if (!response.status) {
        throw new Error(
            response.error?.errorMessage ??
                "Не удалось зарегистрировать уведомления",
        );
    }

    useSettingsStore().firebaseInstallationId = fid;
}

/**
 * Установка подписки на события регистрации Firebase.
 *
 * Подписка устанавливается один раз и сохраняется
 * на протяжении работы PWA.
 */
async function ensureRegistrationListener(): Promise<void> {
    if (unsubscribeRegistration) {
        return;
    }

    const unsubscribe = await Messaging.subscribeToRegistration(
        async (fid) => {
            try {
                await saveFirebaseInstallationId(fid);
            } catch (error) {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Не удалось синхронизировать Firebase Installation ID",
                );
            }
        },
        (fid) => {
            const settingsStore = useSettingsStore();

            if (settingsStore.firebaseInstallationId === fid) {
                settingsStore.firebaseInstallationId = null;
            }
        },
    );

    if (unsubscribe === null) {
        throw new Error(
            "Firebase Messaging недоступен",
        );
    }

    unsubscribeRegistration = unsubscribe;
}

/**
 * Проверка поддержки уведомлений и текущего разрешения браузера.
 *
 * Если разрешение уже выдано, регистрирует экземпляр
 * PWA и синхронизирует FID с сервером.
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
                syncRegistrationInBackground();
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
 * Запрос разрешения и регистрация экземпляра PWA.
 */
async function enableNotifications(): Promise<EnableNotificationsResult> {
    try {
        const permission = await Messaging.requestNotificationPermission();

        if (permission !== "granted") {
            return permission === "denied"
                ? "denied"
                : "unavailable";
        }

        await ensureRegistrationListener();

        const registered = await Messaging.registerForNotifications();

        return registered ? "enabled" : "unavailable";
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

export const NotificationPermission = {
    checkPermission,
    enableNotifications,
};
import {
    deleteToken,
    getMessaging,
    getToken,
    isSupported,
    onMessage,
    type MessagePayload,
    type Messaging,
} from "firebase/messaging";

import { firebaseApp } from "./app";
import { FIREBASE_VAPID_KEY } from "../constants/firebase"

const VAPID_KEY = FIREBASE_VAPID_KEY;

let messagingPromise: Promise<Messaging | null> | null = null;

async function getMessagingInstance(): Promise<Messaging | null> {
    if (messagingPromise === null) {
        messagingPromise = (async () => {
            if (typeof window === "undefined") {
                return null;
            }

            if (!await isSupported()) {
                return null;
            }

            return getMessaging(firebaseApp);
        })();
    }

    return messagingPromise;
}

/**
 * Проверка поддержки Firebase Messaging браузером.
 */
async function isMessagingSupported(): Promise<boolean> {
    if (typeof window === "undefined") {
        return false;
    }

    return isSupported();
}

/**
 * Запрос разрешения на показ уведомлений.
 * Вызывать в ответ на действие пользователя.
 */
async function requestNotificationPermission(): Promise<NotificationPermission> {
    if (typeof window === "undefined" || !("Notification" in window)) {
        return "denied";
    }

    return Notification.requestPermission();
}

/**
 * Получение FCM-токена текущего браузера.
 * Не запрашивает разрешение автоматически.
 */
async function getFcmToken(): Promise<string | null> {
    if (typeof window === "undefined" || !("Notification" in window)) {
        return null;
    }

    if (Notification.permission !== "granted") {
        return null;
    }

    if (!("serviceWorker" in navigator)) {
        return null;
    }

    const messaging = await getMessagingInstance();

    if (messaging === null) {
        return null;
    }

    const registration = await navigator.serviceWorker.getRegistration(
        import.meta.env.BASE_URL,
    );

    if (!registration?.active) {
        throw new Error(
            "Не найден активный Service Worker для PWA",
        );
    }

    return getToken(messaging, {
        vapidKey: VAPID_KEY,
        serviceWorkerRegistration: registration,
    });
}

/**
 * Запрос разрешения и получение FCM-токена.
 */
async function enableNotifications(): Promise<string | null> {
    const permission = await requestNotificationPermission();

    if (permission !== "granted") {
        return null;
    }

    return getFcmToken();
}

/**
 * Удаление FCM-токена этого браузера.
 */
async function disableNotifications(): Promise<boolean> {
    const messaging = await getMessagingInstance();

    if (messaging === null) {
        return false;
    }

    return deleteToken(messaging);
}

/**
 * Подписка на сообщения, полученные при открытой PWA.
 * Возвращает функцию отмены подписки.
 */
async function subscribeToMessages(
    callback: (payload: MessagePayload) => void,
): Promise<(() => void) | null> {
    const messaging = await getMessagingInstance();

    if (messaging === null) {
        return null;
    }

    return onMessage(messaging, callback);
}

export const Messaging = {
    isMessagingSupported,
    requestNotificationPermission,
    getFcmToken,
    enableNotifications,
    disableNotifications,
    subscribeToMessages,
};
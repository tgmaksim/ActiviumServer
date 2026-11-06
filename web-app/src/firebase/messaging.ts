import {
    getMessaging,
    isSupported,
    onMessage,
    onRegistered,
    onUnregistered,
    register,
    unregister,
    type MessagePayload,
    type Messaging as FCMMessaging,
} from "firebase/messaging";

import { firebaseApp } from "./app";
import { FIREBASE_VAPID_KEY } from "../constants/firebase";

const VAPID_KEY = FIREBASE_VAPID_KEY;

let messagingPromise: Promise<FCMMessaging | null> | null = null;

async function getMessagingInstance(): Promise<FCMMessaging | null> {
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
 * Получение активной регистрации Service Worker.
 */
async function getServiceWorkerRegistration(): Promise<ServiceWorkerRegistration | null> {
    if (!("serviceWorker" in navigator)) {
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

    return registration;
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
 * Подписка на изменение состояния регистрации FCM.
 *
 * onRegistered вызывается при регистрации и обновлении FID.
 * onUnregistered вызывается при удалении регистрации.
 *
 * Возвращает функцию отмены обеих подписок.
 */
async function subscribeToRegistration(
    onFidRegistered: (fid: string) => void,
    onFidUnregistered?: (fid: string) => void,
): Promise<(() => void) | null> {
    const messaging = await getMessagingInstance();

    if (messaging === null) {
        return null;
    }

    const unsubscribeRegistered = onRegistered(
        messaging,
        onFidRegistered,
    );

    const unsubscribeUnregistered = onUnregistered(
        messaging,
        (fid) => onFidUnregistered?.(fid),
    );

    return () => {
        unsubscribeRegistered();
        unsubscribeUnregistered();
    };
}

/**
 * Регистрация экземпляра PWA в Firebase Cloud Messaging.
 *
 * FID передаётся через onRegistered(), а не возвращается
 * из этой функции.
 */
async function registerForNotifications(): Promise<boolean> {
    if (
        typeof window === "undefined" ||
        !("Notification" in window) ||
        Notification.permission !== "granted"
    ) {
        return false;
    }

    const messaging = await getMessagingInstance();

    if (messaging === null) {
        return false;
    }

    const registration = await getServiceWorkerRegistration();

    if (registration === null) {
        return false;
    }

    await register(messaging, {
        vapidKey: VAPID_KEY,
        serviceWorkerRegistration: registration,
    });

    return true;
}

/**
 * Запрос разрешения и регистрация экземпляра PWA.
 */
async function enableNotifications(): Promise<boolean> {
    const permission = await requestNotificationPermission();

    if (permission !== "granted") {
        return false;
    }

    return registerForNotifications();
}

/**
 * Отмена регистрации экземпляра PWA в FCM.
 */
async function disableNotifications(): Promise<boolean> {
    const messaging = await getMessagingInstance();

    if (messaging === null) {
        return false;
    }

    await unregister(messaging);

    return true;
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
    subscribeToRegistration,
    registerForNotifications,
    enableNotifications,
    disableNotifications,
    subscribeToMessages,
};
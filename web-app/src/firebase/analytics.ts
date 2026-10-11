import {
    getAnalytics,
    isSupported,
    logEvent,
    setAnalyticsCollectionEnabled,
    setUserId,
    setUserProperties,
    type Analytics,
} from "firebase/analytics";

import { firebaseApp } from "./app";

let analyticsPromise: Promise<Analytics | null> | null = null;

/**
 * Получение экземпляра Firebase Analytics.
 */
async function getAnalyticsInstance(): Promise<Analytics | null> {
    if (typeof window === "undefined") {
        return null;
    }

    if (analyticsPromise === null) {
        analyticsPromise = (async () => {
            if (!await isSupported()) {
                return null;
            }

            return getAnalytics(firebaseApp);
        })();
    }

    return analyticsPromise;
}

/**
 * Проверка поддержки Firebase Analytics.
 */
async function isAnalyticsSupported(): Promise<boolean> {
    if (typeof window === "undefined") {
        return false;
    }

    return isSupported();
}

/**
 * Отправка события аналитики.
 */
async function logAnalyticsEvent(
    eventName: string,
    params?: Record<string, string | number | boolean>,
): Promise<void> {
    const analytics = await getAnalyticsInstance();

    if (analytics === null) {
        return;
    }

    logEvent(analytics, eventName, params);
}

/**
 * Регистрация просмотра экрана.
 */
async function logScreenView(screenName: string): Promise<void> {
    await logAnalyticsEvent("screen_view", {
        firebase_screen: screenName,
        firebase_screen_class: screenName,
    });
}

/**
 * Включение или отключение сбора аналитики.
 */
async function setAnalyticsEnabled(enabled: boolean): Promise<void> {
    const analytics = await getAnalyticsInstance();

    if (analytics === null) {
        return;
    }

    setAnalyticsCollectionEnabled(analytics, enabled);
}

/**
 * Установка идентификатора пользователя для аналитики.
 */
async function setAnalyticsUserId(userId: string | null): Promise<void> {
    const analytics = await getAnalyticsInstance();

    if (analytics === null) {
        return;
    }

    setUserId(analytics, userId);
}

/**
 * Установка пользовательских свойств аналитики.
 */
async function setAnalyticsUserProperties(
    properties: Record<string, string>,
): Promise<void> {
    const analytics = await getAnalyticsInstance();

    if (analytics === null) {
        return;
    }

    setUserProperties(analytics, properties);
}

export const Analytics = {
    isAnalyticsSupported,
    logAnalyticsEvent,
    logScreenView,
    setAnalyticsEnabled,
    setAnalyticsUserId,
    setAnalyticsUserProperties,
};
import "./notifications/click";

import { initializeApp } from "firebase/app";
import {
    getMessaging,
    onBackgroundMessage,
} from "firebase/messaging/sw";

import {
    FIREBASE_API_KEY,
    FIREBASE_AUTH_DOMAIN,
    FIREBASE_PROJECT_ID,
    FIREBASE_STORAGE_BUCKET,
    FIREBASE_MESSAGING_SENDER_ID,
    FIREBASE_APP_ID,
    FIREBASE_MEASUREMENT_ID,
} from "@/constants/firebase";

import { NotificationManager } from "@/notifications/manager";
import type { NotificationPayload } from "@/notifications/types";
import { Utilities } from "@/utils/utils";

import {
    cleanupOutdatedCaches,
    precacheAndRoute,
    createHandlerBoundToURL,
} from "workbox-precaching";
import { registerRoute } from "workbox-routing";
import { clientsClaim } from "workbox-core";

declare let self: ServiceWorkerGlobalScope & {
    __WB_MANIFEST: Array<{
        url: string;
        revision: string | null;
    }>;
};

const firebaseApp = initializeApp({
    apiKey: FIREBASE_API_KEY,
    authDomain: FIREBASE_AUTH_DOMAIN,
    projectId: FIREBASE_PROJECT_ID,
    storageBucket: FIREBASE_STORAGE_BUCKET,
    messagingSenderId: FIREBASE_MESSAGING_SENDER_ID,
    appId: FIREBASE_APP_ID,
    measurementId: FIREBASE_MEASUREMENT_ID,
});

cleanupOutdatedCaches();
precacheAndRoute(self.__WB_MANIFEST);

self.skipWaiting();
clientsClaim();

const homeUrl = new URL(import.meta.env.BASE_URL, self.location.origin);
const fallbackUrl = `${import.meta.env.BASE_URL}index.html`;

registerRoute(
    ({ request, url }) =>
        request.mode === "navigate" &&
        url.origin === self.location.origin &&
        !url.pathname.startsWith(`${homeUrl.pathname}auth`),
    createHandlerBoundToURL(fallbackUrl),
);

const messaging = getMessaging(firebaseApp);

function parsePayload(
    data: Record<string, string>,
): NotificationPayload | null {
    const title = data.title;
    const body = data.body;

    if (!title || !body) {
        return null;
    }

    let buttons: unknown = data.buttons;

    if (typeof buttons === "string") {
        try {
            buttons = JSON.parse(buttons);
        } catch {
            buttons = [];
        }
    }

    return {
        ...data,
        title,
        body,
        ...(data.priority !== undefined
            ? { priority: Number(data.priority) }
            : {}),
        ...(data.time !== undefined
            ? { time: Number(data.time) }
            : {}),
        ...(buttons !== undefined ? { buttons } : {}),
    };
}

onBackgroundMessage(messaging, async (message) => {
    try {
        const data = message.data;

        if (!data) {
            return;
        }

        const payload = parsePayload(data);

        if (!payload) {
            return;
        }

        await NotificationManager.show(self.registration, payload);
    } catch (error) {
        Utilities.log(
            error instanceof Error
                ? error
                : new Error(String(error)),
            "Error at MessagingService.onMessageReceived",
        );
    }
});

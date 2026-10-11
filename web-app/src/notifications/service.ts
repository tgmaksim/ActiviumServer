import { getMessaging, onMessage } from "firebase/messaging";
import { firebaseApp } from "@/firebase/app";
import { NotificationManager } from "./manager";
import type { NotificationPayload } from "./types";

let unsubscribe: (() => void) | undefined;

function parsePayload(
    data: Record<string, string>,
): NotificationPayload | null {
    const title = data.title;
    const body = data.body;

    if (!title || !body) {
        return null;
    }

    let buttons = data.buttons;

    if (buttons) {
        try {
            buttons = JSON.parse(buttons);
        } catch {
            buttons = "[]";
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

export function subscribeToMessages(): () => void {
    unsubscribe?.();

    const messaging = getMessaging(firebaseApp);

    unsubscribe = onMessage(messaging, async (message) => {
        const data = message.data;

        if (!data) {
            return;
        }

        const payload = parsePayload(data);

        if (!payload) {
            return;
        }

        const registration = await navigator.serviceWorker.ready;
        await NotificationManager.show(registration, payload);
    });

    return () => {
        unsubscribe?.();
        unsubscribe = undefined;
    };
}

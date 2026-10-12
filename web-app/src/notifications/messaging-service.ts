import { Messaging } from "@/firebase/messaging";
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
        buttons: NotificationManager.parseButtons(data.buttons),
    };
}

export async function subscribeToMessages(): Promise<(() => void) | null> {
    unsubscribe?.();
    unsubscribe = undefined;

    const stop = await Messaging.subscribeToMessages(async (message) => {
        const payload = parsePayload(message.data ?? {});

        if (!payload) {
            return;
        }

        const registration = await navigator.serviceWorker.ready;
        await NotificationManager.show(registration, payload);
    });

    unsubscribe = stop ?? undefined;

    return () => {
        unsubscribe?.();
        unsubscribe = undefined;
    };
}

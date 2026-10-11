import type {
    NotificationButton,
    NotificationPayload,
} from "./types";
import { routes } from "@/constants/routes";

export class NotificationManager {
    static async show(
        registration: ServiceWorkerRegistration,
        payload: NotificationPayload,
    ): Promise<void> {
        if (typeof Notification === "undefined") {
            return;
        }

        if (Notification.permission !== "granted") {
            return;
        }

        const buttons = this.parseButtons(payload.buttons);

        const data = { ...payload };
        delete data.buttons;

        const buttonData: Record<string, Record<string, string>> = {};

        for (const button of buttons) {
            if (button.data) {
                buttonData[button.action] = button.data;
            }
        }

        await registration.showNotification(payload.title, {
            body: payload.body,
            icon: `${routes.home}icons/logo.png`,
            ...(payload.imageUrl ? { image: payload.imageUrl } : {}),
            ...(payload.time !== undefined
                ? { timestamp: payload.time }
                : {}),
            ...(payload.channelId
                ? { tag: payload.channelId }
                : {}),
            actions: buttons.map((button) => ({
                action: button.action,
                title: button.text,
            })),
            data: {
                ...data,
                buttonData,
            },
        });
    }

    static parseButtons(
        value: unknown,
    ): NotificationButton[] {
        if (typeof value === "string") {
            try {
                value = JSON.parse(value);
            } catch {
                return [];
            }
        }

        if (!Array.isArray(value)) {
            return [];
        }

        return value.filter(
            (button): button is NotificationButton =>
                typeof button === "object" &&
                button !== null &&
                typeof button.text === "string" &&
                typeof button.action === "string",
        );
    }
}

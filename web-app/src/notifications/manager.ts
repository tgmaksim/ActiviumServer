import type {
    NotificationButton,
    NotificationPayload,
    NotificationActionResult,
} from "./types";
import { Utilities } from "@/utils/utils";
import { strings } from "@/constants/strings";
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

        const notificationId = crypto.randomUUID();
        await registration.showNotification(payload.title, {
            body: payload.body,
            icon: `${routes.home}icons/logo.png`,
            ...(payload.imageUrl ? { image: payload.imageUrl } : {}),
            ...(payload.time !== undefined
                ? { timestamp: payload.time }
                : {}),
            tag: `activium-${notificationId}`,
            actions: buttons.map((button) => ({
                action: button.action,
                title: button.text,
            })),
            data: {
                ...data,
                notificationId,
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
            } catch (error) {
                Utilities.log(
                    error instanceof Error
                        ? error
                        : new Error(String(error)),
                    "Error at NotificationManager.parseButtons",
                );
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

    static async showActionResult(
        registration: ServiceWorkerRegistration,
        notificationId: string,
        result: NotificationActionResult,
    ): Promise<void> {
        const messages: Record<NotificationActionResult, string> = {
            success: strings.notificationBroadcastSuccessText,
            failure: strings.notificationBroadcastUnsuccessText,
            unknown: strings.notificationBroadcastUnknownText,
        };

        await registration.showNotification(strings.notificationBroadcastTitle, {
            body: messages[result],
            icon: `${routes.home}icons/logo.png`,
            tag: `activium-${notificationId}`,
            data: {
                notificationId: `result-${notificationId}`,
                type: "action-result",
            },
        });
    }
}

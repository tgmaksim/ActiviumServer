import type { NotificationActionMessage } from "./types";

export function subscribeToNotificationActions(
    handler: (message: NotificationActionMessage) => void,
): () => void {
    const listener = (event: MessageEvent<NotificationActionMessage>) => {
        const message = event.data;

        if (
            message?.type !== "notification-action" ||
            typeof message.action !== "string"
        ) {
            return;
        }

        handler(message);
    };

    navigator.serviceWorker.addEventListener("message", listener);

    // Поддержка сценария, когда PWA открылась из уведомления
    // и параметры действия были переданы через URL.
    const url = new URL(window.location.href);
    const action = url.searchParams.get("notificationAction");
    const rawData = url.searchParams.get("notificationData");

    if (action) {
        let data: Record<string, unknown> = {};

        if (rawData) {
            try {
                data = JSON.parse(rawData);
            } catch {
                data = {};
            }
        }

        handler({
            type: "notification-action",
            action,
            data,
        });

        url.searchParams.delete("notificationAction");
        url.searchParams.delete("notificationData");

        window.history.replaceState({}, "", url);
    }

    return () => {
        navigator.serviceWorker.removeEventListener("message", listener);
    };
}

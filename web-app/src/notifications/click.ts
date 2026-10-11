import { handleNotificationAction } from "./NotificationActionReceiver";

self.addEventListener("notificationclick", (event: NotificationEvent) => {
    event.notification.close();

    event.waitUntil(
        (async () => {
            const notificationData =
                (event.notification.data ?? {}) as Record<string, unknown>;

            const action = event.action || "open";

            const buttonData = notificationData.buttonData as
                | Record<string, Record<string, string>>
                | undefined;

            const data = {
                ...notificationData,
                ...(buttonData?.[action] ?? {}),
            };

            delete data.buttonData;

            await handleNotificationAction(action, data);
        })(),
    );
});

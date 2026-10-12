import { handleNotificationAction } from "./receiver";
import { Utilities } from "@/utils/utils";
import {
    handleNotificationAction as executeNotificationAction,
} from "./action";

self.addEventListener("notificationclick", (event: NotificationEvent) => {
    event.notification.close();

    event.waitUntil(
        (async () => {
            try {
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

                if (action === "open") {
                    await handleNotificationAction(action, data);
                } else {
                    await executeNotificationAction(
                        action,
                        data,
                        self.registration,
                    );
                }
            } catch (error) {
                Utilities.log(
                    error,
                    "Error at NotificationActionReceiver.onReceive",
                );
            }
        })(),
    );
});

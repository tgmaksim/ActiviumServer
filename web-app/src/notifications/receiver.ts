import { routes } from "@/constants/routes";

export async function handleNotificationAction(
    action: string,
    data: Record<string, unknown>,
): Promise<void> {
    const clients = await self.clients.matchAll({
        type: "window",
        includeUncontrolled: true,
    });

    const message = {
        type: "notification-action",
        action,
        data,
    };

    // Если приложение уже открыто — передаём ему действие.
    for (const client of clients) {
        client.postMessage(message);

        if ("focus" in client) {
            await client.focus();
            return;
        }
    }

    // Иначе открываем приложение и передаём действие через URL.
    const url = new URL(routes.home, self.location.origin);
    url.searchParams.set("notificationAction", action);
    url.searchParams.set(
        "notificationData",
        JSON.stringify(data),
    );

    await self.clients.openWindow(url.toString());
}

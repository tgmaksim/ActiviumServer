export interface NotificationButton {
    text: string;
    action: string;
    data?: Record<string, string>;
}

export interface NotificationPayload {
    title: string;
    body: string;
    channelId?: string;
    imageUrl?: string;
    priority?: number;
    time?: number;
    buttons?: NotificationButton[];

    // Остальные поля FCM, например childId, ratingKey,
    // subject, place и параметры перехода.
    [key: string]: unknown;
}

export interface NotificationActionMessage {
    type: "notification-action";
    action: string;
    data: Record<string, unknown>;
}

export type NotificationActionResult =
    | "success"
    | "failure"
    | "unknown";

import { DnevnikTools } from "@/api/dtools";
import { Settings } from "@/api/settings";
import { NotificationManager } from "./manager";
import { Utilities } from "@/utils/utils";
import type { NotificationActionResult } from "./types";

export async function handleNotificationAction(
    action: string,
    data: Record<string, unknown>,
    registration: ServiceWorkerRegistration,
): Promise<void> {
    const notificationId = String(
        data.notificationId ?? crypto.randomUUID(),
    );

    let result: NotificationActionResult = "unknown";

    try {
        switch (action) {
            case "praise": {
                const ratingKey =
                    typeof data.ratingKey === "string"
                        ? data.ratingKey
                        : null;

                const lessonKey =
                    typeof data.lessonKey === "string"
                        ? data.lessonKey
                        : null;

                if (ratingKey === null && lessonKey === null) {
                    return;
                }

                const response = await DnevnikTools.sendPraise(
                    lessonKey,
                    ratingKey,
                    typeof data.text === "string" ? data.text : null,
                );

                result = response.status ? "success" : "failure";
                break;
            }

            case "hide_extracurricular_activity": {
                const childId = Number(data.profile);
                const subject = data.subject;
                const place = data.place;

                if (
                    !Number.isInteger(childId) ||
                    childId <= 0 ||
                    typeof subject !== "string" ||
                    typeof place !== "string"
                ) {
                    return;
                }

                const response =
                    await Settings.hideExtracurricularActivity(
                        childId,
                        subject,
                        place,
                    );

                result = response.status ? "success" : "failure";
                break;
            }

            default:
                break;
        }
    } catch (error) {
        Utilities.log(
            error,
            "Coroutine Error at NotificationActionReceiver.runAsyncAction",
        );

        result = "failure";
    }

    await NotificationManager.showActionResult(
        registration,
        notificationId,
        result,
    );
}

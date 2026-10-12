/**
 * Утилиты приложения.
 */

function log(string: string | null, tag: string): void;
function log(error: string): void;
function log(error: Error, context?: string): void;

function log(
    value: string | Error | null,
    tagOrContext?: string,
): void {
    // Обычное информационное сообщение.
    if (tagOrContext !== undefined && !(value instanceof Error)) {
        console.debug(`Activium.${tagOrContext}`, String(value));
        return;
    }

    // Логирование исключения.
    if (value instanceof Error) {
        console.error(
            "Activium.error",
            tagOrContext ?? "",
            value,
        );

        // Firebase Crashlytics не поддерживается в Web SDK.
        return;
    }

    // Логирование текстовой ошибки.
    console.error("Activium.error", value);
}

export const Utilities = {
    log,
};
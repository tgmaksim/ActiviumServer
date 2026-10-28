/**
 * Утилиты приложения.
 */

import { showToast } from "@/composables/useToast";

import { strings } from "@/constants/strings";
import type { UiText } from "@/types/ui-text";

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

function showText(
    text: string,
    long: boolean = false
): void {
    showToast(text, long ? "long" : "short");
}

/**
 * Показывает UI-сообщение, представленное ресурсной
 * или динамической строкой.
 */
function showUiMessage(
    message: UiText,
    long: boolean = false,
): void {
    if (message.type === "dynamicString") {
        showText(message.value, long);
        return;
    }

    const resource = strings[message.key];

    const value =
        typeof resource === "function"
            ? Reflect.apply(resource, undefined, [...(message.args ?? [])])
            : resource;

    if (typeof value !== "string") {
        log(
            `Ресурс "${String(message.key)}" не вернул строку`,
            "showUiMessage",
        );
        return;
    }

    showText(value, long);
}

export const Utilities = {
    log,
    showText,
    showUiMessage,
};
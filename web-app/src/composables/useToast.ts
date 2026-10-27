import { ref } from "vue";

export type ToastDuration = "short" | "long";

interface ToastMessage {
    id: number;
    message: string;
    duration: ToastDuration;
}

const SHORT_DURATION = 2_000;
const LONG_DURATION = 3_500;

const currentToast = ref<ToastMessage | null>(null);
const toastQueue: ToastMessage[] = [];

let nextToastId = 0;

/**
 * Показать Toast.
 *
 * Если другой Toast уже отображается,
 * сообщение добавляется в конец очереди.
 */
export function showToast(
    message: string,
    duration: ToastDuration = "short",
): void {
    const normalizedMessage = message.trim();

    if (!normalizedMessage) {
        return;
    }

    const toast: ToastMessage = {
        id: ++nextToastId,
        message: normalizedMessage,
        duration,
    };

    if (currentToast.value === null) {
        currentToast.value = toast;
        return;
    }

    toastQueue.push(toast);
}

/**
 * Завершить показ текущего Toast
 * и перейти к следующему сообщению.
 */
export function dismissToast(id: number): void {
    if (currentToast.value?.id !== id) {
        return;
    }

    currentToast.value = toastQueue.shift() ?? null;
}

/**
 * Длительность показа Toast в миллисекундах.
 */
export function getToastDuration(duration: ToastDuration): number {
    return duration === "long"
        ? LONG_DURATION
        : SHORT_DURATION;
}

export { currentToast };
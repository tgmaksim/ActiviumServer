import { useSettingsStore } from "@/stores/settings";

type InstallOutcome =
    | "accepted"
    | "dismissed"
    | "unavailable";

export type PwaPlatform =
    | "android"
    | "ios"
    | "other";

interface BeforeInstallPromptEvent extends Event {
    prompt(): Promise<void>;

    userChoice: Promise<{
        outcome: "accepted" | "dismissed";
        platform: string;
    }>;
}

let deferredInstallPrompt:
    BeforeInstallPromptEvent | null = null;

window.addEventListener(
    "beforeinstallprompt",
    (event: Event) => {
        event.preventDefault();

        deferredInstallPrompt =
            event as BeforeInstallPromptEvent;
    },
);

window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
});

export function getPwaPlatform(): PwaPlatform {
    const userAgent = navigator.userAgent;

    if (/android/i.test(userAgent)) {
        return "android";
    }

    // iPadOS может представляться как macOS.
    const isAppleMobile =
        /iPad|iPhone|iPod/i.test(userAgent) ||
        (
            navigator.platform === "MacIntel" &&
            navigator.maxTouchPoints > 1
        );

    if (isAppleMobile) {
        return "ios";
    }

    return "other";
}

/**
 * Проверяет, запущено ли приложение
 * в установленном режиме.
 */
export function isRunningAsInstalledPwa(): boolean {
    const isStandalone =
        window.matchMedia(
            "(display-mode: standalone)",
        ).matches;

    const isIosStandalone = (
        navigator as Navigator & {
            standalone?: boolean;
        }
    ).standalone === true;

    return isStandalone || isIosStandalone;
}

/**
 * Проверяет, нужно ли предлагать установку.
 */
export function shouldShowInstallPrompt(): boolean {
    if (isRunningAsInstalledPwa()) {
        return false;
    }

    const settingsStore = useSettingsStore();

    return !settingsStore.installPromptHiddenKey;
}

/**
 * Запускает системную установку, если она доступна.
 */
export async function promptPwaInstall():
    Promise<InstallOutcome> {
    if (!deferredInstallPrompt) {
        return "unavailable";
    }

    const installEvent = deferredInstallPrompt;

    try {
        await installEvent.prompt();

        const choice = await installEvent.userChoice;

        deferredInstallPrompt = null;

        return choice.outcome;
    } catch (error) {
        Utilities.log(
            error,
            "Не удалось запустить установку PWA"
        );

        return "unavailable";
    }
}

/**
 * Больше не показывать предложение установки.
 */
export function hideInstallPrompt(): void {
    const settingsStore = useSettingsStore();
    settingsStore.installPromptHiddenKey = true;
}
import { watch } from "vue";

import { useSettingsStore } from "@/stores/settings";

/**
 * Инициализирует применение темы на уровне всего приложения.
 *
 * Восстанавливает сохранённую тему при запуске и применяет
 * последующие изменения настройки darkTheme.
 */
export function initializeTheme(): void {
    const settingsStore = useSettingsStore();

    watch(
        () => settingsStore.darkTheme,
        (isDark) => {
            document.documentElement.classList.toggle("dark", isDark);
        },
        {
            immediate: true,
            flush: "sync",
        },
    );
}
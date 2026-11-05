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

            const metaThemeColor = document.querySelector('meta[name="theme-color"]');
            if (metaThemeColor) {
                metaThemeColor.setAttribute('content', isDark ? "#001C38" : "#B3E5FC");
            }
        },
        {
            immediate: true,
            flush: "sync",
        },
    );
}
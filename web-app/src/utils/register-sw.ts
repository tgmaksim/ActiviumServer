import { registerSW } from "virtual:pwa-register";

const UPDATE_CHECK_INTERVAL = 5 * 60 * 1000;

export function initializeSW(): void {
    registerSW({
        immediate: true,

        onRegisteredSW(_swUrl, registration) {
            if (!registration) {
                return;
            }

            // Проверка актуальности при запуске приложения
            void registration.update().catch((error: unknown) => {
                Utilities.log(error, "Не удалось проверить обновление");
            });

            // Повторная проверка, если приложение долго открыто
            window.setInterval(() => {
                void registration.update().catch((error: unknown) => {
                    Utilities.log(error, "Не удалось проверить обновление");
                });
            }, UPDATE_CHECK_INTERVAL);
        },

        onRegisterError(error) {
            Utilities.log(error, "Не удалось зарегистрировать Service Worker");
        },
    });
}
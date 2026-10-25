import { createApp } from "vue";
import { createPinia } from "pinia";
import { registerSW } from "virtual:pwa-register";

import App from "./App.vue";
import router from "./router";

import { launch } from "./bootstrap/launcher";
import "./style.css";

import { Utilities } from "@/utils/utils";

const initialRoute = launch();

const UPDATE_CHECK_INTERVAL = 5 * 60 * 1000;

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

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");

router.isReady().then(() => {
    if (router.currentRoute.value.path !== initialRoute) {
        router.replace(initialRoute);
    }
});